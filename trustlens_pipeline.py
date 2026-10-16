"""TrustLens APAC: bounded multi-agent fraud/scam analysis pipeline.

Google Cloud setup:
  gcloud auth application-default login
  gcloud config set project YOUR_PROJECT_ID
  pip install google-genai pydantic tenacity

Environment:
  export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
  export GOOGLE_CLOUD_LOCATION=global
  export GEMINI_MODEL=gemini-2.5-flash  # or another model enabled in your project

This is a prototype reference. It deliberately does not connect to a bank,
move money, freeze accounts, or make an autonomous financial decision.
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_AGENT_CALLS = 5
MAX_RETRIES = 2

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)


# ---------------------------------------------------------------------------
# Schemas: every agent returns a constrained object, never free-form text.
# ---------------------------------------------------------------------------

RiskBand = Literal["low", "review", "high"]


class EvidenceItem(BaseModel):
    id: str
    kind: Literal["text", "visual", "transaction", "url", "rule"]
    claim: str
    quote: str = ""
    confidence: float = Field(ge=0.0, le=1.0)


class EvidenceExtraction(BaseModel):
    language: str
    message_text: str
    sender_claim: str
    requested_actions: list[str]
    urls: list[str]
    entities: list[str]
    urgency_signals: list[str]
    evidence: list[EvidenceItem]
    uncertainty: list[str]


class PatternMatch(BaseModel):
    name: Literal[
        "impersonation",
        "credential_harvesting",
        "suspicious_link",
        "fake_refund",
        "remote_access",
        "urgency_pressure",
        "none",
    ]
    matched: bool
    rationale: str
    evidence_ids: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class PatternAnalysis(BaseModel):
    matches: list[PatternMatch]
    uncertainty: list[str]


class PolicyFinding(BaseModel):
    policy_id: str
    rule: str
    safe_action: str
    prohibited_actions: list[str]
    source_excerpt: str


class PolicyAnalysis(BaseModel):
    findings: list[PolicyFinding]
    human_review_required: bool


class RiskSynthesis(BaseModel):
    risk_band: RiskBand
    confidence: float = Field(ge=0.0, le=1.0)
    scam_patterns: list[str]
    evidence_ids: list[str]
    rationale: list[str]
    recommended_action: str
    prohibited_actions: list[str]
    human_review_required: bool
    uncertainty: list[str]


class UserCommunication(BaseModel):
    language: str
    headline: str
    explanation: str
    next_steps: list[str]
    do_not_do: list[str]
    disclaimer: str


class TrustLensResult(BaseModel):
    case_id: str
    risk: RiskSynthesis
    communication: UserCommunication
    audit: dict[str, Any]


# ---------------------------------------------------------------------------
# Grounding corpus. Replace this with Vertex AI Search or a governed datastore
# in production. Keep source IDs in every policy finding for auditability.
# ---------------------------------------------------------------------------

POLICY_KB = [
    {
        "id": "policy-otp-001",
        "keywords": {"otp", "one-time", "password", "verification code", "pin"},
        "text": "Never share a one-time password, PIN, password, or verification code with a caller or message sender. Contact the institution through an independently verified official channel.",
    },
    {
        "id": "policy-link-001",
        "keywords": {"link", "click", "url", "login", "verify"},
        "text": "Do not click a suspicious link or enter credentials after following an unsolicited message. Open the official application or type the official domain yourself.",
    },
    {
        "id": "policy-remote-001",
        "keywords": {"remote", "anydesk", "teamviewer", "screen", "install"},
        "text": "Do not install remote-access software or share your screen to receive a refund or resolve an account issue.",
    },
    {
        "id": "policy-refund-001",
        "keywords": {"refund", "cashback", "fee", "release", "payment"},
        "text": "A refund or cashback request should not require a customer to disclose credentials or send money to receive money.",
    },
]


def retrieve_policies(extraction: EvidenceExtraction) -> list[dict[str, str]]:
    """Small deterministic grounding retriever for the prototype."""
    corpus = " ".join(
        [
            extraction.message_text,
            *extraction.requested_actions,
            *extraction.urgency_signals,
            *extraction.urls,
        ]
    ).lower()
    scored = []
    for item in POLICY_KB:
        score = sum(1 for keyword in item["keywords"] if keyword in corpus)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        {"id": item["id"], "text": item["text"]}
        for _, item in scored[:4]
    ]


# ---------------------------------------------------------------------------
# Gemini call helper
# ---------------------------------------------------------------------------


def ask_gemini(
    *,
    agent_name: str,
    system_instruction: str,
    prompt: str,
    schema: type[BaseModel],
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
) -> BaseModel:
    """Call Gemini with JSON-schema constrained output and bounded retries."""
    contents: list[Any] = [prompt]
    if image_bytes:
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=image_mime_type or "image/jpeg",
            )
        )

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=schema,
                    max_output_tokens=4096,
                ),
            )
            # response.text is JSON because response_mime_type is application/json.
            parsed = schema.model_validate(json.loads(response.text))
            return parsed
        except (ValidationError, json.JSONDecodeError, Exception) as exc:
            last_error = exc
            if attempt == MAX_RETRIES:
                break

    raise RuntimeError(f"Agent {agent_name} failed after retries: {last_error}")


# ---------------------------------------------------------------------------
# Safety controls. These are deterministic and run after Gemini.
# ---------------------------------------------------------------------------

FORBIDDEN_RECOMMENDATION_TERMS = [
    "share your otp",
    "share the otp",
    "send your password",
    "send your pin",
    "install remote access",
    "give remote access",
    "click the link to verify",
]


def apply_safety_guard(
    extraction: EvidenceExtraction,
    risk: RiskSynthesis,
) -> RiskSynthesis:
    """Enforce non-negotiable safety behavior independently of the model."""
    combined = " ".join(
        [risk.recommended_action, *risk.prohibited_actions]
    ).lower()

    if any(term in combined for term in FORBIDDEN_RECOMMENDATION_TERMS):
        risk.risk_band = "high"
        risk.human_review_required = True
        risk.recommended_action = (
            "Do not share credentials or send money. Contact the institution "
            "through an independently verified official channel."
        )
        risk.prohibited_actions = [
            "Do not share an OTP, PIN, password, or verification code.",
            "Do not click an unsolicited link.",
            "Do not install remote-access software.",
        ]
        risk.rationale.append("Safety guard replaced an unsafe generated recommendation.")

    # High-signal deterministic rules override a weak model classification.
    corpus = (
        extraction.message_text
        + " "
        + " ".join(extraction.requested_actions)
        + " "
        + " ".join(extraction.urgency_signals)
    ).lower()
    high_signal = [
        term
        for term in ["otp", "one-time password", "pin", "remote access", "anydesk"]
        if term in corpus
    ]
    if len(high_signal) >= 1:
        risk.human_review_required = True
    if len(high_signal) >= 2:
        risk.risk_band = "high"
        risk.confidence = max(risk.confidence, 0.90)

    return risk


# ---------------------------------------------------------------------------
# Specialized agents
# ---------------------------------------------------------------------------


def evidence_agent(message: str, image_bytes: bytes | None) -> EvidenceExtraction:
    return ask_gemini(
        agent_name="evidence",
        schema=EvidenceExtraction,
        image_bytes=image_bytes,
        system_instruction=(
            "You are TrustLens Evidence Agent. Extract only observable facts. "
            "Do not decide whether the message is fraudulent. Do not invent sender identity. "
            "Return concise evidence IDs that downstream agents can cite."
        ),
        prompt=(
            "Analyze this user-submitted message and optional screenshot. "
            "Extract language, exact message text, claimed sender, requested actions, URLs, "
            "entities, urgency signals, and evidence items. Preserve uncertainty.\n\n"
            f"TEXT INPUT:\n{message or '[none]'}"
        ),
    )


def pattern_agent(extraction: EvidenceExtraction) -> PatternAnalysis:
    return ask_gemini(
        agent_name="pattern",
        schema=PatternAnalysis,
        system_instruction=(
            "You are TrustLens Scam Pattern Agent. Compare evidence to known scam patterns. "
            "Only mark a pattern matched when the evidence supports it. Cite evidence IDs."
        ),
        prompt=(
            "Classify the following extracted evidence. Consider impersonation, credential "
            "harvesting, suspicious link, fake refund, remote access, and urgency pressure.\n\n"
            + extraction.model_dump_json(indent=2)
        ),
    )


def policy_agent(
    extraction: EvidenceExtraction,
    retrieved_policies: list[dict[str, str]],
) -> PolicyAnalysis:
    return ask_gemini(
        agent_name="policy",
        schema=PolicyAnalysis,
        system_instruction=(
            "You are TrustLens Policy Agent. Ground every finding in the supplied policy excerpts. "
            "Never invent banking policy. Always require human review when evidence is incomplete "
            "or the user could lose money or credentials."
        ),
        prompt=(
            "Create grounded safety findings. Every policy_id must come from the supplied corpus.\n\n"
            f"EXTRACTED EVIDENCE:\n{extraction.model_dump_json(indent=2)}\n\n"
            f"RETRIEVED POLICY EXCERPTS:\n{json.dumps(retrieved_policies, indent=2)}"
        ),
    )


def synthesis_agent(
    extraction: EvidenceExtraction,
    patterns: PatternAnalysis,
    policies: PolicyAnalysis,
) -> RiskSynthesis:
    return ask_gemini(
        agent_name="synthesis",
        schema=RiskSynthesis,
        system_instruction=(
            "You are TrustLens Risk Synthesis Agent. Produce a conservative, explainable risk "
            "assessment. Use only supplied evidence, pattern matches, and policy findings. "
            "A review result is preferred over an unsupported high-confidence claim. "
            "Never provide an action that shares credentials, sends money, clicks suspicious links, "
            "or installs remote-access software."
        ),
        prompt=(
            "Synthesize the final risk assessment. Cite evidence IDs in evidence_ids. "
            "Use risk_band low, review, or high.\n\n"
            f"EVIDENCE:\n{extraction.model_dump_json(indent=2)}\n\n"
            f"PATTERN ANALYSIS:\n{patterns.model_dump_json(indent=2)}\n\n"
            f"POLICY ANALYSIS:\n{policies.model_dump_json(indent=2)}"
        ),
    )


def communication_agent(
    language: str,
    risk: RiskSynthesis,
) -> UserCommunication:
    return ask_gemini(
        agent_name="communication",
        schema=UserCommunication,
        system_instruction=(
            "You are TrustLens Communication Agent. Explain the result plainly and calmly. "
            "Do not shame the user. Do not claim certainty. Preserve every safety warning."
        ),
        prompt=(
            f"Write a concise user-facing explanation in language '{language}'. "
            "The disclaimer must say this is an educational prototype and the user should "
            "contact the institution through an independently verified official channel.\n\n"
            + risk.model_dump_json(indent=2)
        ),
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


@dataclass
class CaseInput:
    message: str
    image_path: str | None = None
    requested_language: str = "en"


def load_image(path: str | None) -> tuple[bytes | None, str | None]:
    if not path:
        return None, None
    data = Path(path).read_bytes()
    mime, _ = mimetypes.guess_type(path)
    if mime not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Only JPEG, PNG, and WebP screenshots are accepted")
    if len(data) > 8 * 1024 * 1024:
        raise ValueError("Screenshot exceeds the 8 MB prototype limit")
    return data, mime


def run_trustlens(case: CaseInput) -> TrustLensResult:
    """Run the bounded TrustLens pipeline.

    Agent budget:
      1 evidence + 2 parallel analysis + 1 synthesis + 1 communication = 5 calls.
    """
    image_bytes, image_mime = load_image(case.image_path)
    case_id = f"TL-{uuid.uuid4().hex[:10].upper()}"

    # Agent 1: multimodal evidence extraction.
    extraction = evidence_agent(case.message, image_bytes)

    # Deterministic retrieval happens outside the model.
    retrieved = retrieve_policies(extraction)

    # Agents 2 and 3 are independent after extraction and can run concurrently.
    with ThreadPoolExecutor(max_workers=2) as pool:
        pattern_future = pool.submit(pattern_agent, extraction)
        policy_future = pool.submit(policy_agent, extraction, retrieved)
        patterns = pattern_future.result()
        policies = policy_future.result()

    # Agent 4: risk synthesis, followed immediately by deterministic guardrails.
    risk = synthesis_agent(extraction, patterns, policies)
    risk = apply_safety_guard(extraction, risk)

    # Agent 5: localized user communication.
    language = case.requested_language or extraction.language or "en"
    communication = communication_agent(language, risk)

    # Server-side invariant: never return a result without an evidence trail.
    if not risk.evidence_ids and risk.risk_band != "low":
        risk.risk_band = "review"
        risk.human_review_required = True
        risk.uncertainty.append("No evidence citation was returned; forced human review.")
    
    return TrustLensResult(
        case_id=case_id,
        risk=risk,
        communication=communication,
        audit={
            "model": MODEL,
            "agent_budget": MAX_AGENT_CALLS,
            "grounding_sources": [p["id"] for p in retrieved],
            "image_analyzed": image_bytes is not None,
            "human_review_required": risk.human_review_required,
            "prototype_notice": "Synthetic/demo workflow; not a banking decision engine.",
        },
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the TrustLens pipeline")
    parser.add_argument("message", help="Suspicious message text")
    parser.add_argument("--image", help="Optional screenshot path")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()

    result = run_trustlens(
        CaseInput(
            message=args.message,
            image_path=args.image,
            requested_language=args.language,
        )
    )
    print(result.model_dump_json(indent=2))


# Example:
# python trustlens_pipeline.py \
#   "Your bank refund is pending. Share your OTP and click http://example.test" \
#   --image ./screenshot.png --language en
#
# Cloud Run entrypoint integration (inside your FastAPI route):
# result = run_trustlens(CaseInput(message=body.message, image_path=tmp_path))
# return result.model_dump(mode="json")

# Production substitutions:
# - Replace retrieve_policies() with Vertex AI Search / governed retrieval.
# - Store evidence and audit events in Cloud Storage and Firestore.
# - Put this function behind Cloud Run and Firebase Authentication.
# - Add Firebase App Check, request authentication, rate limits, and deletion TTLs.
# - Keep real banking actions outside this prototype and behind separate human-approved APIs.
