Team

TrustForge AI

TrustForge AI builds responsible, explainable AI solutions that help people make safer decisions in high-risk digital environments.

For the AI Builder Cup, our team created TrustLens APAC: a Google Cloud and Gemini-powered scam-prevention assistant that analyzes suspicious payment messages and screenshots, identifies evidence-backed risk signals, recommends safe next steps, and routes uncertain cases to human review.

## Live Demo

- **Dashboard**: https://trustlens-dashboard-993487022253.us-central1.run.app/live_product.html
- **API docs**: https://trustlens-api-993487022253.us-central1.run.app/docs
- **Health check**: https://trustlens-api-993487022253.us-central1.run.app/health

Try it: open the dashboard and click **Analyze Live** below the slide. The button calls the real Gemini 2.5 Flash pipeline and displays the structured risk analysis inline.



Team positioning: We use generative AI where semantic reasoning creates value, and deterministic software where safety and control matter most.

The problem

Digital-payment scams combine social engineering with technical deception. A single message can imitate a trusted institution, create urgency, request a one-time password, redirect a refund, or ask a user to install remote-access software.

The user needs a clear next action. A support analyst needs a traceable explanation rather than an opaque model score. TrustLens focuses on the narrow, high-value intervention between receiving a suspicious message and making an irreversible decision:


Turn confusing evidence into a safe and explainable next step before money or credentials are exposed.

What TrustLens does

TrustLens accepts suspicious text and optional screenshots. It extracts observable evidence with Gemini, compares the evidence with grounded scam-pattern policies, synthesizes a conservative risk band, applies deterministic safety rules, and explains the recommended next step in the userâ€™s selected language.

Core capabilities

Capability
What the prototype demonstrates
Text analysis
Accepts suspicious messages or transaction context.
Multimodal analysis
Accepts JPEG, PNG, and WebP screenshots up to 8 MB.
Evidence extraction
Identifies claimed sender, requested actions, urgency signals, URLs, entities, and evidence references.
Scam-pattern reasoning
Evaluates impersonation, credential harvesting, suspicious links, fake refunds, remote access, and urgency pressure.
Grounded policy guidance
Retrieves relevant safety policies from a versioned prototype corpus.
Conservative risk bands
Returns low, review, or high; this is not a production fraud probability.
Deterministic safety guard
Prevents unsafe recommendations such as sharing an OTP or installing remote-access software.
Human review
Routes high-risk, ambiguous, or unsupported cases to review.
Localized communication
Generates plain-language next steps in the selected language.
Audit metadata
Returns model, grounding-source, image-analysis, and review-status metadata.




Product experience

The dashboard is designed for a fast, judgeable workflow:

1.
Paste a suspicious message or click Use example.

2.
Optionally upload a synthetic screenshot.

3.
Select the explanation language.

4.
Click Analyze safely.

5.
Review the risk band, confidence, rationale, evidence, policy action, prohibited actions, and uncertainty.

6.
Demonstrate the human-review handoff.

7.
Expand the raw API response and audit trace.

Why this is different from a generic chatbot

1.
Evidence-first: Every rationale points back to extracted evidence identifiers.

2.
Policy-grounded: Recommendations are connected to safety policies and prohibited actions.

3.
Safety-invariant: Deterministic Python logic can override unsafe model advice.

4.
Human-bound: High-risk, ambiguous, or unsupported cases explicitly stop at human review.

5.
Multimodal: The same pipeline can reason over the text a user types and the screenshot a user receives.

Architecture

mermaid

Source



Runtime sequence

1.
Intake: Next.js sends text or multipart screenshot input to FastAPI.

2.
Evidence extraction: Gemini identifies language, sender claims, requested actions, URLs, entities, urgency signals, and evidence items.

3.
Parallel analysis: Pattern analysis and policy analysis run independently after extraction.

4.
Risk synthesis: Gemini produces a structured risk object with evidence IDs, rationale, recommended action, prohibited actions, uncertainty, and review status.

5.
Safety enforcement: A deterministic guard checks the generated recommendation and can force human review or replace unsafe advice.

6.
Communication: Gemini produces localized, plain-language guidance.

7.
Response: The dashboard renders the result and audit metadata.

The reference implementation is intentionally bounded to a maximum of five model calls. It does not connect to a bank, move money, freeze accounts, or perform autonomous financial actions.

Technology stack

Frontend

â€¢
Next.js 14 App Router.

â€¢
React 18.

â€¢
TypeScript.

â€¢
Responsive CSS Modules.

â€¢
Browser fetch client for text and multipart API requests.

Backend

â€¢
Python 3.11.

â€¢
FastAPI.

â€¢
Pydantic structured response models.

â€¢
Google Gen AI Python SDK.

â€¢
Gemini through Vertex AI.

â€¢
Deterministic post-generation safety guard.

Google Cloud

â€¢
Cloud Run for the API container.

â€¢
Artifact Registry for container images.

â€¢
Cloud Build for image builds.

â€¢
Vertex AI for Gemini inference.

â€¢
Optional production path: Firestore for case state and Cloud Storage for consented evidence with retention TTLs.

CI/CD

â€¢
GitHub Actions.

â€¢
GitHub OIDC.

â€¢
Google Cloud Workload Identity Federation.

â€¢
Immutable container tags based on Git commit SHA.

â€¢
Cloud Run health-check smoke test after deployment.

Repository structure
.
├── README.md
├── app.py # FastAPI backend
├── trustlens_pipeline.py # Bounded Gemini orchestration
├── requirements.txt # Backend dependencies
├── Dockerfile # Backend container image
├── cloudrun-service.yaml # Cloud Run manifest template
├── deploy-cloud-run.sh # Direct gcloud deployment
├── deploy-trustlens-end-to-end.ps1 # End-to-end PowerShell automation
├── bootstrap-github-wif.ps1 # WIF bootstrap helper
├── package.json # Next.js scaffold (not deployed)
├── next.config.js
├── tsconfig.json
├── TrustLens APAC_ Judges' Guide.md
├── TrustLens APAC_ Architecture and Sequence.md
├── TrustLens APAC_ Responsible AI and Privacy.md
├── TrustLens APAC_ Evaluation Plan.md
├── TrustLens APAC_ Submission Checklist.md
├── TrustLens APAC_ Three-Minute Demo Script.md
└── trustlens-dashboard/
├── Dockerfile # Nginx container image
├── index.html # Redirect to live_product.html
├── live_product.html # Dashboard UI + live API test button
├── problem.html
├── solution.html
├── impact.html
├── genai_depth.html
└── responsible_ai.html

text

Local setupLocal setup

Prerequisites

â€¢
Python 3.11 or later.

â€¢
Node.js 20 or later.

â€¢
Google Cloud CLI.

â€¢
A Google Cloud project with Vertex AI enabled.

â€¢
Application Default Credentials configured.

â€¢
A Gemini model enabled in the selected region.

Backend installation

Bash


python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt



Authenticate with Google Cloud:

Bash


gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID



Configure the backend:

Bash


export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export GEMINI_MODEL="gemini-2.5-flash"
export PORT="8080"



Start the API:

Bash


uvicorn app:app --host 0.0.0.0 --port 8080 --reload



The local API will be available at:

Plain Text


http://localhost:8080



OpenAPI documentation:

Plain Text


http://localhost:8080/docs



Frontend installation

Bash


cd trustlens-dashboard
npm install



Create trustlens-dashboard/.env.local:

Bash


NEXT_PUBLIC_TRUSTLENS_API_URL=http://localhost:8080



Start the dashboard:

Bash


npm run dev



Open:

Plain Text


http://localhost:3000



Validate the production build:

Bash


npm run build



API usage

Health check

Bash


curl http://localhost:8080/health



Response:

JSON


{"status":"ok"}



Text analysis

Bash


curl -X POST http://localhost:8080/v1/analyze/text \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Your refund is pending. Share your OTP and click http://example.test to release the money.",
    "language": "en"
  }'



Screenshot analysis

Use a synthetic screenshot only:

Bash


curl -X POST http://localhost:8080/v1/analyze/multipart \
  -F 'message=Your refund is pending. Share your OTP.' \
  -F 'language=en' \
  -F 'screenshot=@./screenshot.png'



Response shape

JSON


{
  "case_id": "TL-ABC123",
  "risk": {
    "risk_band": "high",
    "confidence": 0.91,
    "scam_patterns": ["credential_harvesting", "fake_refund"],
    "evidence_ids": ["e1", "e2"],
    "rationale": ["The sender requests a one-time password."],
    "recommended_action": "Do not share credentials. Contact the institution using an independently verified channel.",
    "prohibited_actions": ["Do not share an OTP."],
    "human_review_required": true,
    "uncertainty": []
  },
  "communication": {
    "language": "en",
    "headline": "Stop before sharing your code",
    "explanation": "The message contains multiple high-risk indicators.",
    "next_steps": ["Open the official banking application directly."],
    "do_not_do": ["Do not click the unsolicited link."],
    "disclaimer": "This is an educational prototype."
  },
  "audit": {
    "model": "gemini-2.5-flash",
    "agent_budget": 5,
    "grounding_sources": ["policy-otp-001"],
    "image_analyzed": false,
    "human_review_required": true,
    "prototype_notice": "Synthetic/demo workflow; not a banking decision engine."
  }
}



Deploy directly to Cloud Run

From the repository root:

Bash


export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
./deploy-cloud-run.sh



The direct deployment script:

1.
Enables required Google Cloud APIs.

2.
Creates an Artifact Registry repository.

3.
Builds and pushes the container with Cloud Build.

4.
Creates the runtime service account if needed.

5.
Grants Vertex AI access.

6.
Deploys the Cloud Run service.

7.
Prints the service URL.

The default direct deployment enables unauthenticated invocation for the hackathon demo. For production, remove public invocation and use authenticated access.

One-command PowerShell automation

After installing and authenticating gcloud, gh, and git, run from the repository root:

Plain Text


Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass



Plain Text


.\deploy-trustlens-end-to-end.ps1 `
    -ProjectId "YOUR_GCP_PROJECT_ID" `
    -GitHubRepository "YOUR_GITHUB_ORG/YOUR_REPOSITORY" `
    -Region "us-central1" `
    -GeminiModel "gemini-2.5-flash" `
    -Push `
    -RunDeployment



This automation bootstraps WIF, configures GitHub variables and secrets through GitHub CLI, commits and pushes the workflow, dispatches GitHub Actions, and allows the workflow to deploy Cloud Run.

Read the full setup guide: trustlens-docs/GITHUB_ACTIONS_CICD.md.

CI/CD validation commands

Backend syntax:

Bash


python -m py_compile trustlens_pipeline.py app.py



Frontend production build:

Bash


cd trustlens-dashboard
npm ci
npm run build



Deployment health check:

Bash


curl -f "$SERVICE_URL/health"



Evaluation plan

TrustLens is evaluated on synthetic or fully consented cases only. The evaluation plan covers:

â€¢
Six scam patterns.

â€¢
Text and screenshot inputs.

â€¢
Multiple languages.

â€¢
Ambiguous cases.

â€¢
Adversarial safety cases.

â€¢
High-risk recall.

â€¢
Unsafe-action rate.

â€¢
Evidence citation coverage.

â€¢
Schema validity.

â€¢
Human-review routing.

â€¢
Latency and screenshot processing success.

Prototype targets are not production guarantees. Observed results must be recorded only after running the deployed service against a versioned dataset.

See trustlens-docs/EVALUATION_PLAN.md.

Responsible AI and safety boundaries

TrustLens is an educational hackathon prototype for assisted scam prevention.

It must not:

â€¢
Move or authorize money.

â€¢
Freeze, close, or restrict an account.

â€¢
Make credit, insurance, employment, or eligibility decisions.

â€¢
Identify a person as a criminal based only on model output.

â€¢
Request or encourage sharing an OTP, PIN, password, or verification code.

â€¢
Encourage clicking an unsolicited link.

â€¢
Encourage installing remote-access software.

â€¢
Contact a bank, telecom provider, or law-enforcement agency without an authorized workflow.

The current dashboardâ€™s analyst review controls demonstrate the workflow locally. A production version should persist authenticated review actions in Firestore with authorization, timestamps, reason codes, ownership, and immutable audit events.

Uploaded screenshots are temporary in the current backend and are deleted after analysis. Do not use real customer data, account numbers, credentials, or payment information in the demo.

See trustlens-docs/RESPONSIBLE_AI.md.

Judge quick start

1.
Open the deployed dashboard.

2.
Click Use example.

3.
Click Analyze safely.

4.
Observe the high-risk result and evidence rationale.

5.
Review the recommended next step and prohibited actions.

6.
Open the human-review flow.

7.
Expand the raw API response and audit trace.

8.
Upload a synthetic screenshot to demonstrate multimodal analysis.

For the complete narration, see trustlens-docs/DEMO_SCRIPT.md and trustlens-docs/SPEAKER_NOTES.md.

Project documentation

All documentation is included as markdown files in the repository root:

- TrustLens APAC_ Judges' Guide.md
- TrustLens APAC_ Architecture and Sequence.md
- TrustLens APAC_ Responsible AI and Privacy.md
- TrustLens APAC_ Evaluation Plan.md
- TrustLens APAC_ Submission Checklist.md
- TrustLens APAC_ Three-Minute Demo Script.md
- TrustLens APAC — Speaker Notes and Pitch Script.md
- TrustLens APAC.md

Hackathon alignmentHackathon alignment

TrustLens APAC is designed for the BFSI: Intelligent Risk, Fraud & Financial Experiences theme.

The project demonstrates:

â€¢
Gemini multimodal analysis.

â€¢
Structured, bounded multi-agent orchestration.

â€¢
Grounded policy reasoning.

â€¢
Deterministic safety enforcement.

â€¢
Human-in-the-loop escalation.

â€¢
Cloud Run deployment.

â€¢
A practical consumer and analyst workflow.

Official program pages:

â€¢


AI Builder Cup overview

â€¢


Themes and requirements

â€¢


Rewards

â€¢


FAQs

Project status

This is a hackathon prototype. The following production hardening remains before real financial-sector use:

â€¢
Governed retrieval through Vertex AI Search or an equivalent reviewed data store.

â€¢
Authenticated Cloud Run invocation.

â€¢
Firebase Authentication and role-based analyst access.

â€¢
Firestore case state and immutable review events.

â€¢
Encrypted Cloud Storage with retention and deletion TTLs.

â€¢
Prompt-injection and red-team testing.

â€¢
Dependency, vulnerability, privacy, and model-risk review.

â€¢
Operational monitoring, alerting, rate limits, and abuse controls.

License and data notice

This repository is intended for evaluation and educational use. It must not be used as a production financial decision system without security, privacy, compliance, model-risk, and operational review.

Use synthetic or fully consented data only. Never commit secrets, credentials, real OTPs, account numbers, identity numbers, or customer screenshots.


