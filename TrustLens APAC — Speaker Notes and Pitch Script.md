# TrustLens APAC — Speaker Notes and Pitch Script

## Delivery profile

**Recommended duration:** 3 minutes 30 seconds to 4 minutes.

**Delivery style:** Calm, direct, evidence-led, and technically confident. Do not read every word on the slide. Use the slide as visual proof while the narration supplies the causal story.

**Core narrative:** A scam message creates a high-pressure decision. TrustLens turns the message or screenshot into evidence, grounds the interpretation in policy, applies a deterministic safety boundary, and gives the user or analyst a safe next step without taking an irreversible financial action.

**Opening promise:** “Before a scam becomes a transaction, TrustLens makes the safe next step obvious.”

**Closing promise:** “TrustLens uses Gemini where semantic reasoning creates value, and deterministic software where safety and control matter.”

## Timing map

| Slide | Title | Target time |
|---:|---|---:|
| 1 | TrustLens APAC | 0:20 |
| 2 | The moment before the loss | 0:23 |
| 3 | From confusing message to safe action | 0:25 |
| 4 | A decision-support layer, not another chatbot | 0:25 |
| 5 | Bounded agents. Google Cloud backbone. | 0:30 |
| 6 | The product judges can use | 0:25 |
| 7 | Where Gemini creates real leverage | 0:25 |
| 8 | Designed to measure what matters | 0:22 |
| 9 | Safe by design | 0:25 |
| 10 | Make the safe next step obvious | 0:15 |
| **Total** |  | **3:55** |

## Slide 1 — TrustLens APAC

### On-slide purpose
Establish the product, theme, and one-line promise immediately.

### Speaker notes
“TrustLens APAC is our submission for the BFSI: Intelligent Risk, Fraud and Financial Experiences theme. We focus on the moment before a scam becomes a transaction. Our promise is simple: make the safe next step obvious before a user shares credentials or sends money.”

### Emphasis
- Say “before a scam becomes a transaction” slowly.
- Identify TrustLens as an assisted-prevention system, not an autonomous banking system.

### Transition
“To see why this matters, look at what one ordinary scam message asks a user to decide.”

## Slide 2 — The moment before the loss

### On-slide purpose
Make the problem concrete and emotionally legible without using real customer data.

### Speaker notes
“A scam is not just a bad message. It is a high-pressure decision compressed into a few seconds. The example combines four signals: an institution impersonation, urgency, a request for an OTP, and a redirect to an unsolicited link. A user may not know which clues matter. A support analyst may receive only a screenshot. Both need a safe, evidence-backed interpretation.”

### Emphasis
- Point to the four signal blocks in order.
- Do not imply that the system identifies criminal intent; say it identifies observable risk signals.

### Transition
“TrustLens is designed around that gap between confusing evidence and a safe action.”

## Slide 3 — From confusing message to safe action

### On-slide purpose
Explain the complete product workflow in a single visual.

### Speaker notes
“The workflow has four stages. First, the user pastes a message or uploads a screenshot. Second, Gemini normalizes the evidence: claimed sender, URLs, urgency, requested actions, and evidence references. Third, pattern analysis and policy grounding produce a structured risk synthesis. Finally, a deterministic guard checks the recommendation, and the communication layer explains the safe next step in the selected language. If the case is high-risk, uncertain, or unsupported, the system stops at human review.”

### Emphasis
- Make clear that the safety guard runs after generation, before the response is returned.
- Mention the five-call bounded budget only if time permits.

### Transition
“That architecture creates a different product from a generic financial chatbot.”

## Slide 4 — A decision-support layer, not another chatbot

### On-slide purpose
State the four differentiators that make the project technically and responsibly distinctive.

### Speaker notes
“TrustLens is evidence-first: every rationale points back to evidence identifiers. It is policy-grounded: recommendations are tied to safety rules and prohibited actions. It is safety-invariant: ordinary Python logic can override unsafe model advice involving OTPs, passwords, links, or remote access. And it is human-bound: high-risk, ambiguous, or unsupported cases are explicitly escalated. We use generative reasoning where it creates leverage, and deterministic software where control matters more than fluency.”

### Emphasis
- The final sentence is the thesis of the presentation.
- Pause after “human-bound.”

### Transition
“Here is how that principle is implemented on Google Cloud.”

## Slide 5 — Bounded agents. Google Cloud backbone.

### On-slide purpose
Prove technical depth, Google Cloud usage, and system control.

### Speaker notes
“The browser dashboard calls a FastAPI service on Cloud Run. The first Gemini call performs multimodal evidence extraction. After that, pattern analysis and policy analysis run independently and can execute in parallel. A synthesis agent creates the risk object, the Python safety guard validates and can override it, and a final communication agent localizes the explanation. Every agent returns a constrained object rather than free-form prose. The current reference pipeline has a maximum of five model calls and no connectivity to banking actions.”

### Emphasis
- Trace the diagram left to right with your pointer.
- Call out Vertex AI or Gemini through Vertex AI, Cloud Run, and the policy retrieval layer.
- Explain that parallelism is a design choice, not a claim of autonomous behavior.

### Transition
“The result is not just an architecture diagram; it is a judgeable product.”

## Slide 6 — The product judges can use

### On-slide purpose
Connect the architecture to a concrete user experience.

### Speaker notes
“The judge flow is intentionally short. Paste a synthetic suspicious message, optionally upload a screenshot, select a language, and click Analyze safely. The result shows the risk band, confidence indicator, rationale, scam-pattern tags, recommended next step, prohibited actions, uncertainty, evidence count, grounding count, and review status. The analyst controls demonstrate the handoff boundary. In production, those controls would persist authenticated decisions and audit events; in this prototype, they make the workflow visible without pretending to be a production case-management system.”

### Emphasis
- If demonstrating live, click the example and show the result.
- Point specifically to “Do not share an OTP” or equivalent safe action.

### Transition
“Gemini is doing meaningful work behind that simple surface.”

## Slide 7 — Where Gemini creates real leverage

### On-slide purpose
Show that AI is central, purposeful, and technically constrained.

### Speaker notes
“Gemini creates leverage in four places. It reads both text and screenshots, so the system can analyze what a user actually receives. It returns structured objects that can be validated by software. It separates semantic pattern analysis from policy analysis, which makes the workflow inspectable and testable. And it generates localized, plain-language communication while preserving explicit do-not-do warnings. This is not a chat wrapper around a fixed classifier; it is a bounded multimodal reasoning pipeline.”

### Emphasis
- Mention schema-constrained outputs and Pydantic validation.
- Avoid claiming perfect translation or universal language coverage.

### Transition
“We also designed the project so the safety claim can be measured rather than asserted.”

## Slide 8 — Designed to measure what matters

### On-slide purpose
Present credible evaluation without inventing results.

### Speaker notes
“Our evaluation plan uses a versioned synthetic dataset with at least thirty cases across six scam patterns, text and screenshot inputs, multiple languages, ambiguous cases, and adversarial safety tests. We measure high-risk recall, unsafe-action rate, evidence citation coverage, schema validity, human-review routing, latency, and screenshot success. The numbers shown here are prototype targets, not observed production results. Before submission, we will replace any target with an actual measured value only after running the deployed service.”

### Emphasis
- Be explicit that targets are not performance claims.
- The strongest safety metric is zero unsafe-action rate in the evaluated set.

### Transition
“Measurement matters because responsible AI is not a disclaimer added after the build.”

## Slide 9 — Safe by design

### On-slide purpose
Make the safety boundary unmistakable.

### Speaker notes
“TrustLens always shows evidence and uncertainty, escalates high-risk or unsupported cases, and never moves money, freezes an account, requests an OTP, or contacts a bank autonomously. Uploaded screenshots are temporary in the current prototype and should be synthetic or consented. A production deployment would add authenticated invocation, role-based analyst access, encrypted evidence storage, retention TTLs, and immutable audit events. The boundary is part of the product design: TrustLens assists interpretation; it does not make an irreversible financial decision.”

### Emphasis
- Say the prohibited actions as a short list.
- This slide is important for risk-sensitive judges; do not rush it.

### Transition
“That is the standard we want to bring to the moment before a scam becomes a transaction.”

## Slide 10 — Make the safe next step obvious

### On-slide purpose
Close with a memorable product promise and clear submission proof.

### Speaker notes
“TrustLens brings grounded Gemini reasoning, deterministic safety, and human oversight to one high-value moment: before a scam becomes a transaction. The submission is verifiable through the live Cloud Run prototype, public source documentation, and the short demo path. TrustLens does not promise to replace a bank’s fraud systems. It promises to help a person take the safer next step sooner.”

### Final line
“TrustLens makes the safe next step visible, grounded, and auditable.”

## Optional 30-second technical Q&A extension

“If you want the implementation detail: the browser calls FastAPI on Cloud Run; the backend uses the Google Gen AI SDK through Vertex AI; the pipeline has evidence, pattern, policy, synthesis, guard, and communication stages; responses are Pydantic-constrained; and unsupported non-low-risk responses are forced into human review. The production path would add governed retrieval, Firestore case state, Cloud Storage with TTL deletion, authentication, and observability.”

## Optional answer to ‘Why should this win?’

“Because it is narrow enough to demonstrate, technically deep enough to evaluate, and responsible enough to trust. The core insight is not simply to classify a scam. It is to connect evidence to policy, policy to a safe action, and uncertainty to a human boundary.”

## Presenter checklist

- Use synthetic examples only.
- Do not claim observed accuracy until the evaluation run is complete.
- Say “risk band” or “triage signal,” not “fraud probability.”
- Demonstrate the safe action and prohibited actions, not just the headline score.
- Point out the deterministic guard and human-review flag.
- Mention Gemini, Vertex AI, Cloud Run, and the structured-output contract.
- Keep the final sentence short and memorable.
