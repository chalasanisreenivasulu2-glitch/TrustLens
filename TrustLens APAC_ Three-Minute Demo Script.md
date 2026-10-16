# TrustLens APAC: Three-Minute Demo Script

## Demo objective

Demonstrate a complete, deployed, end-to-end workflow in under three minutes. The judge should see the problem, Gemini’s meaningful role, grounded evidence, safety controls, human review, and Google Cloud deployment.

## Before recording

Use synthetic data only. Confirm that the Cloud Run API is healthy and the frontend points to the deployed API.

Recommended test message:

> Your bank refund is pending. Share your OTP and click http://example.test to release the money.

Prepare one screenshot showing the same message. Keep the browser on the TrustLens dashboard.

## Timeline

| Time | Presenter action | Narration | Judging signal |
|---:|---|---|---|
| 0:00–0:20 | Show the dashboard and paste the example message. | “Scams often use urgency, fake refunds, and requests for verification codes. TrustLens helps a user choose the safe next step before money or credentials are exposed.” | Clear problem and user value. |
| 0:20–0:35 | Select English and upload the synthetic screenshot. | “The same case can arrive as text or a screenshot. We use Gemini multimodal extraction to normalize the evidence.” | Meaningful GenAI and multimodal usage. |
| 0:35–0:55 | Click **Analyze safely**. Show loading state. | “The workflow is bounded: evidence extraction, parallel pattern and policy analysis, risk synthesis, deterministic safety guard, and localized communication.” | Technical architecture. |
| 0:55–1:20 | Show the result card. | “The system identifies a high-risk case and shows confidence, rationale, and evidence references. It does not expose a black-box score alone.” | Explainability and UX. |
| 1:20–1:40 | Point to recommended next step and prohibited actions. | “The safe action is to avoid sharing the OTP and contact the institution through an independently verified channel. The safety guard prevents unsafe advice such as sharing credentials or installing remote-access software.” | Responsible AI and deterministic controls. |
| 1:40–1:58 | Point to the human-review banner. | “High-risk or uncertain cases require human review. TrustLens assists a decision; it does not freeze an account, send money, or contact a bank.” | Appropriate autonomy boundary. |
| 1:58–2:20 | Click **Approve handoff** or **Correct finding**. | “An analyst can correct or approve the handoff. In a production version, this action would become an authenticated Firestore audit event.” | Workflow completion and roadmap. |
| 2:20–2:40 | Expand the raw API response and audit trace. | “The response is schema-constrained and exposes model, grounding sources, image analysis status, and human-review status.” | Technical merit and auditability. |
| 2:40–2:55 | Show Cloud Run URL or deployment console screenshot. | “The API is deployed as a container on Google Cloud Run and uses Gemini through Vertex AI.” | Required Google Cloud deployment. |
| 2:55–3:00 | Show evaluation slide. | “On synthetic cases, we measure high-risk recall, unsafe-action rate, evidence citation coverage, schema validity, latency, and review routing.” | Measurable impact and scalability. |

## Recovery plan

If the live model call is slow, explain the bounded stages and use the prepared result screenshot. If the API is unavailable, show the raw synthetic response and Cloud Run service configuration. If screenshot upload fails, switch to the text endpoint and state that the multimodal path was validated separately.

## Closing sentence

> **TrustLens makes the safest next step visible, grounded, and auditable before a scam becomes a transaction.**
