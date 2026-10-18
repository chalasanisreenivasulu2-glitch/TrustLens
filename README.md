# TrustLens APAC

## Team

**TrustForge AI** builds responsible, explainable AI solutions that help people make safer decisions in high-risk digital environments.

For the AI Builder Cup, our team created TrustLens APAC: a Google Cloud and Gemini-powered scam-prevention assistant that analyzes suspicious payment messages and screenshots, identifies evidence-backed risk signals, recommends safe next steps, and routes uncertain cases to human review.

## Live Demo

- **Dashboard**: https://trustlens-dashboard-993487022253.us-central1.run.app/live_product.html
- **API docs**: https://trustlens-api-993487022253.us-central1.run.app/docs
- **Health check**: https://trustlens-api-993487022253.us-central1.run.app/health

Try it: open the dashboard and click **Analyze Live** below the slide. The button calls the real Gemini 2.5 Flash pipeline and displays the structured risk analysis inline.

Team positioning: We use generative AI where semantic reasoning creates value, and deterministic software where safety and control matter most.

## The Problem

Digital-payment scams combine social engineering with technical deception. A single message can imitate a trusted institution, create urgency, request a one-time password, redirect a refund, or ask a user to install remote-access software.

The user needs a clear next action. A support analyst needs a traceable explanation rather than an opaque model score. TrustLens focuses on the narrow, high-value intervention between receiving a suspicious message and making an irreversible decision:

> Turn confusing evidence into a safe and explainable next step before money or credentials are exposed.

## What TrustLens Does

TrustLens accepts suspicious text and optional screenshots. It extracts observable evidence with Gemini, compares the evidence with grounded scam-pattern policies, synthesizes a conservative risk band, applies deterministic safety rules, and explains the recommended next step in the user's selected language.

### Core Capabilities

| Capability | What the prototype demonstrates |
|---|---|
| Text analysis | Accepts suspicious messages or transaction context. |
| Multimodal analysis | Accepts JPEG, PNG, and WebP screenshots up to 8 MB. |
| Evidence extraction | Identifies claimed sender, requested actions, urgency signals, URLs, entities, and evidence references. |
| Scam-pattern reasoning | Evaluates impersonation, credential harvesting, suspicious links, fake refunds, remote access, and urgency pressure. |
| Grounded policy guidance | Retrieves relevant safety policies from a versioned prototype corpus. |
| Conservative risk bands | Returns low, review, or high; this is not a production fraud probability. |
| Deterministic safety guard | Prevents unsafe recommendations such as sharing an OTP or installing remote-access software. |
| Human review | Routes high-risk, ambiguous, or unsupported cases to review. |
| Localized communication | Generates plain-language next steps in the selected language. |
| Audit metadata | Returns model, grounding-source, image-analysis, and review-status metadata. |

## Product Experience

The dashboard is designed for a fast, judgeable workflow:

1. Paste a suspicious message into the text area.
2. Select the explanation language.
3. Click **Analyze Live**.
4. Review the risk band, confidence, rationale, evidence, policy action, prohibited actions, and uncertainty in the JSON response.
5. Observe the `human_review_required` flag for high-risk cases.
6. Open the `/docs` endpoint to inspect the full API contract.

## Why This Is Different from a Generic Chatbot

1. **Evidence-first**: Every rationale points back to extracted evidence identifiers.
2. **Policy-grounded**: Recommendations are connected to safety policies and prohibited actions.
3. **Safety-invariant**: Deterministic Python logic can override unsafe model advice.
4. **Human-bound**: High-risk, ambiguous, or unsupported cases explicitly stop at human review.
5. **Multimodal**: The same pipeline can reason over the text a user types and the screenshot a user receives.

## Runtime Sequence

1. **Intake**: Dashboard client sends text or multipart screenshot input to FastAPI.
2. **Evidence extraction**: Gemini identifies language, sender claims, requested actions, URLs, entities, urgency signals, and evidence items.
3. **Parallel analysis**: Pattern analysis and policy analysis run independently after extraction.
4. **Risk synthesis**: Gemini produces a structured risk object with evidence IDs, rationale, recommended action, prohibited actions, uncertainty, and review status.
5. **Safety enforcement**: A deterministic guard checks the generated recommendation and can force human review or replace unsafe advice.
6. **Communication**: Gemini produces localized, plain-language guidance.
7. **Response**: The dashboard renders the result and audit metadata.

The reference implementation is intentionally bounded to a maximum of five model calls. It does not connect to a bank, move money, freeze accounts, or perform autonomous financial actions.

## Technology Stack

### Backend

- Python 3.11
- FastAPI
- Pydantic structured response models
- Google Gen AI Python SDK
- Gemini 2.5 Flash through Vertex AI
- Deterministic post-generation safety guard

### Frontend

- Static HTML dashboard served by Nginx on Cloud Run
- Vanilla JavaScript `fetch()` client calling the live API (the "Analyze Live" panel on `live_product.html`)
- Responsive CSS inlined per page
- Note: a Next.js scaffold exists in the repo (`package.json`, `next.config.js`) but the deployed demo is the static HTML version, chosen for reliability during the hackathon

### Google Cloud

- Cloud Run for the API container and dashboard
- Artifact Registry for container images
- Cloud Build for image builds
- Vertex AI for Gemini inference

## Repository Structure
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
├── README.md
├── app.py # FastAPI backend
├── trustlens_pipeline.py # Bounded Gemini orchestration
├── requirements.txt # Backend dependencies
├── Dockerfile # Backend container image
├── deploy-cloud-run.sh # Deployment script
└── trustlens-dashboard/
├── Dockerfile # Nginx container image
├── index.html # Redirect to live_product.html
├── live_product.html # Dashboard UI + live API test button
├── problem.html
├── solution.html
├── impact.html
├── genai_depth.html
└── responsible_ai.html



