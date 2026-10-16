# TrustLens APAC: Submission Checklist

## Official requirements

- [ ] Team contains two to four members during the building phase.
- [ ] Every member is at least 21 years old.
- [ ] Every member is based in the JAPAC region.
- [ ] No student is included in the team.
- [ ] Team submits exactly one solution under exactly one theme.
- [ ] Project is fresh and built during the official hackathon timeline.
- [ ] Solution uses Google AI models, Google Cloud AI tools, or an allowed Google agentic platform.
- [ ] Prototype is deployed on Google Cloud through Cloud Run, Firebase, or the specified eligible path.
- [ ] Submission materials are in English.

Verify the latest organizer instructions at the official [AI Builder Cup FAQ](https://aibuildercup.com/Faqs.html) before submitting. The pages have shown date inconsistencies; use the latest organizer announcement as the source of truth.

## Required artifacts

### 1. Deployed prototype

- [ ] Cloud Run URL works without a local environment.
- [ ] `/healthz` returns `{"status":"ok"}`.
- [ ] Dashboard loads on desktop and mobile viewport.
- [ ] Text case completes successfully.
- [ ] Screenshot case completes successfully.
- [ ] Risk result, rationale, recommended action, and review flag are visible.
- [ ] Prototype disclaimer is visible.
- [ ] API does not expose credentials or stack traces.

### 2. Public GitHub repository

- [ ] Repository is public and contains the exact deployed code.
- [ ] README includes setup, architecture, API contract, deployment, limitations, and demo steps.
- [ ] No secrets, tokens, customer data, or private URLs are committed.
- [ ] `.gitignore` and `.dockerignore` are present.
- [ ] Dependencies are pinned or version-bounded.
- [ ] A commit tag identifies the submission build.
- [ ] Cloud Run image digest or source commit is recorded.

### 3. Demonstration video under three minutes

- [ ] Video is public on YouTube, Vimeo, or the organizer-approved location.
- [ ] The deployed URL or dashboard is visible.
- [ ] Text analysis is shown.
- [ ] Screenshot or multimodal capability is shown.
- [ ] Grounded explanation and evidence trail are shown.
- [ ] Deterministic safety guard and human-review boundary are explained.
- [ ] Google Cloud deployment is identified.
- [ ] No real personal or financial data appears.
- [ ] Video remains below the organizer’s three-minute limit.

Use [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) as the recording plan.

### 4. Solution deck converted to PDF

Recommended 10-slide structure:

1. **Title:** TrustLens APAC and one-sentence promise.
2. **Problem:** Scam message, user risk, support-team friction.
3. **User journey:** Before money or credentials are exposed.
4. **Solution:** Intake, evidence, policy, risk, safe action, human review.
5. **Live product:** Dashboard screenshots and deployed URL.
6. **Architecture:** Gemini, Cloud Run, frontend, policy grounding, safety guard.
7. **GenAI depth:** Multimodal extraction, bounded agents, structured output, localization.
8. **Impact and evaluation:** Synthetic dataset, metrics, actual observed results.
9. **Responsible AI:** Limitations, human oversight, privacy, prohibited actions.
10. **Scale path:** Banks, wallets, telecoms, remittances, and production hardening.

Do not include invented performance numbers. Use `TBD` until actual evaluation results are recorded.

## Final pre-submission smoke test

```bash
# Backend syntax
python3 -m py_compile trustlens_pipeline.py app.py

# Frontend production build
cd trustlens-dashboard
npm install
npm run build

# Deployed endpoint
curl -f "$SERVICE_URL/healthz"

# Text analysis
curl -f -X POST "$SERVICE_URL/v1/analyze/text" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Your refund is pending. Share your OTP.","language":"en"}'
```

## Submission metadata record

Complete this table immediately before submission:

| Field | Value |
|---|---|
| Team name | TBD |
| Theme | BFSI: Intelligent Risk, Fraud & Financial Experiences |
| Product name | TrustLens APAC |
| Public prototype URL | TBD |
| Public GitHub URL | TBD |
| Public video URL | TBD |
| PDF deck URL/upload | TBD |
| Cloud project region | asia-southeast1 or actual region |
| Cloud Run service | trustlens-api |
| Gemini model | Actual deployed model |
| Source commit | Actual submission commit |
| Evaluation dataset version | Actual version |
| Observed metrics | Actual measured results |

## Last-minute risk controls

- [ ] Disable or remove any demo path that sends real messages or performs real financial actions.
- [ ] Revoke temporary credentials and remove local `.env` files before publishing.
- [ ] Confirm the public URL does not expose debug endpoints or stack traces.
- [ ] Confirm all screenshots and video data are synthetic.
- [ ] Confirm the chosen Gemini model is available in the deployed region.
- [ ] Confirm the demo has a fallback recording or screenshots if the live service is unavailable.
