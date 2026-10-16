# TrustLens APAC: Judges’ Guide

## One-sentence pitch

**TrustLens APAC turns suspicious payment messages and screenshots into a grounded, explainable, and safe next step before a user shares credentials or sends money.**

## The problem

A scam message can combine a trusted-looking identity, urgency, a fake refund, a suspicious link, or a request for a one-time password. A user needs immediate guidance, but a generic chatbot is not enough: the system must show what evidence it used, what policy supports the recommendation, where uncertainty remains, and when a human must decide.

TrustLens addresses this gap through assisted prevention. It does not attempt to replace a bank’s transaction controls. It helps the user and support analyst reach a safer decision earlier.

## The solution in one minute

1. The user pastes a suspicious message or uploads a screenshot.
2. Gemini extracts observable text, entities, URLs, urgency signals, and requested actions.
3. A pattern agent checks a bounded set of scam patterns.
4. A grounded policy agent retrieves relevant safety rules.
5. A synthesis agent produces a schema-constrained risk band and cites evidence.
6. A deterministic guard overrides unsafe recommendations.
7. A communication agent explains the result in the selected language.
8. High-risk or uncertain cases are routed to human review.

## What is genuinely generative

Generative AI is used for multimodal evidence extraction, semantic scam-pattern interpretation, grounded risk synthesis, and localized communication. It is not used as a decorative chat layer.

Every model response is constrained by a Pydantic schema. The final output must contain a risk band, confidence, rationale, evidence identifiers, safe action, prohibited actions, human-review flag, and uncertainty list.

## Technical merit evidence

| Design decision | Why it matters to judges |
|---|---|
| Specialized bounded agents | Clear responsibilities, testable outputs, and predictable call budget. |
| Parallel pattern and policy analysis | Lower latency without sacrificing separation of concerns. |
| Structured output | Makes model output safe for UI and downstream validation. |
| Deterministic guard | Safety-critical behavior does not depend only on model compliance. |
| Grounding corpus | Recommendations reference versioned policy IDs and excerpts. |
| Multimodal input | Demonstrates Gemini vision and real-world evidence handling. |
| Cloud Run | Containerized, managed Google Cloud deployment. |
| Responsive dashboard | Makes the complete workflow judgeable in a live demo. |

## Impact model

The immediate impact is safer user behavior: the user is warned not to share a code, click a suspicious link, send money to receive money, or install remote-access software.

The operational impact is support-team efficiency: an analyst receives normalized evidence, rationale, policy references, uncertainty, and a draft handoff instead of a raw screenshot alone.

The scale path is intentionally credible. The same pattern can extend to banks, digital wallets, telecom fraud teams, remittance providers, and cross-border scam reporting, while keeping final account action under institution-owned controls.

## Innovation

TrustLens is differentiated from a generic financial assistant in four ways:

1. **Evidence-first output:** each risk finding is connected to evidence identifiers.
2. **Policy-grounded action:** the recommendation is grounded in a safety corpus instead of being free-form advice.
3. **Decision boundary:** the system knows when to stop and request human review.
4. **Safety invariant:** deterministic rules prevent dangerous recommendations even if a model response is unsafe.

## UX design

The dashboard uses a two-panel judge flow. The left panel captures text, language, and screenshot input. The right panel displays assessment, confidence, rationale, recommended action, prohibited actions, uncertainty, evidence count, grounding count, and raw audit metadata.

The interface is designed to be understandable in a short live demonstration. The primary action is always “Analyze safely,” and the prototype disclaimer remains visible.

## Questions judges may ask

### Is this a fraud probability model?

No. It returns conservative risk bands for a prototype workflow. It is not calibrated for production fraud probability and should not be used to make autonomous financial decisions.

### Why use multiple agents?

The agents separate extraction, pattern interpretation, policy grounding, synthesis, and communication. This provides observability and testability. It also makes it easier to replace a component without making the entire workflow autonomous.

### What happens when the model is wrong?

Schema validation catches malformed output. Deterministic rules override unsafe actions. Missing evidence citations force review. Conflicting or uncertain cases are explicitly routed to a human.

### What data did you use?

The prototype is designed for synthetic or consented data. The repository should include synthetic cases and labels, not real customer data.

### Does the analyst button persist a decision?

In the current judge-facing frontend, review buttons demonstrate the workflow locally. Production implementation would persist reviewer decisions in authenticated Firestore records with immutable audit events.

### Why Cloud Run?

The API is packaged as a container and deployed as a managed Cloud Run service. This gives the judge a real deployed endpoint and a simple scale path without requiring a cluster.

## The strongest judge takeaway

TrustLens uses Gemini where semantic and multimodal reasoning creates value, and uses deterministic software where safety and control matter. That separation is the core design principle.
