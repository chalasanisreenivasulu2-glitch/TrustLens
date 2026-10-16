# TrustLens APAC: Responsible AI and Privacy

## Intended use

TrustLens is an educational hackathon prototype for assisted scam prevention. It supports a user or analyst in interpreting suspicious payment evidence. It is not a bank decision engine, a fraud probability model, a legal determination, or a substitute for an institution’s official fraud channel.

## Prohibited use

TrustLens must not:

- Move or authorize money.
- Freeze, close, or restrict an account.
- Make credit, insurance, employment, or eligibility decisions.
- Identify a person as a criminal based only on model output.
- Request or encourage sharing of an OTP, PIN, password, or verification code.
- Encourage clicking an unsolicited link.
- Encourage installation of remote-access software.
- Contact a bank, telecom provider, or law-enforcement agency without an authorized human and institution-owned workflow.

## Human oversight

High-risk, uncertain, conflicting, or unsupported cases are routed to human review. The result explicitly exposes uncertainty and includes a review flag. The analyst interaction in the current dashboard is a prototype demonstration; a production implementation must persist decisions with authenticated user identity, authorization, timestamps, reason codes, and immutable audit records.

## Deterministic safety invariants

The system does not rely only on a prompt instruction to produce safe advice. A Python safety guard runs after model synthesis and before the response is sent to the user. It checks for dangerous recommendations and replaces them with a conservative safe action.

If no evidence identifiers are returned for a non-low-risk result, the pipeline forces `review` and marks human review as required. This prevents an unsupported risk statement from appearing as a final decision.

## Data policy for the hackathon

Use synthetic or fully consented data only. Do not place real account numbers, OTPs, passwords, identity numbers, or payment credentials in the repository, demo video, screenshots, logs, or issue tracker.

The current backend stores an uploaded screenshot only in the Cloud Run instance’s temporary filesystem during processing and deletes it after analysis. It does not provide durable case storage. This is appropriate for a limited prototype but not a production retention design.

A production version should:

- Encrypt evidence at rest and in transit.
- Store only the minimum data necessary.
- Apply short retention periods and automatic deletion.
- Separate evidence access from model-service access.
- Restrict analyst access by role and case ownership.
- Redact sensitive values before persistence and logging.
- Provide a user-visible deletion and support path.

## Model limitations

Gemini can misunderstand an image, misread a sender identity, overgeneralize a scam pattern, or produce an incomplete explanation. TrustLens therefore combines model output with structured schemas, grounded excerpts, deterministic rules, uncertainty fields, and human review.

The confidence field is not a calibrated probability. It is a model-produced confidence indicator for prototype triage and must not be presented as a production fraud likelihood.

## Localization

The interface allows language selection and asks the communication agent to produce plain-language guidance. Before production use, each supported language requires human review for safety terminology, cultural clarity, and preservation of prohibited-action warnings.

## Responsible demo language

Use this sentence during the presentation:

> “TrustLens helps a user or analyst interpret evidence; it does not make an irreversible financial decision.”

## Security roadmap

The next security increments are authenticated Cloud Run invocation, Firebase App Check, per-user rate limiting, structured security logs, secret and credential scanning, dependency updates, prompt-injection testing, and red-team cases for unsafe recommendations.
