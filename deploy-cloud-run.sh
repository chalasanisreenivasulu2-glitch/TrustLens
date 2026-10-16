#!/usr/bin/env bash
set -Eeuo pipefail

# Usage:
#   PROJECT_ID=my-project REGION=asia-southeast1 ./deploy-cloud-run.sh
#
# Prerequisites:
#   gcloud auth login
#   gcloud auth application-default login
#   gcloud config set project "$PROJECT_ID"
#   Required APIs are enabled by this script.

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID to your Google Cloud project ID}"
REGION="${REGION:-asia-southeast1}"
REPOSITORY="${REPOSITORY:-trustlens}"
SERVICE="${SERVICE:-trustlens-api}"
RUNTIME_SA="${RUNTIME_SA:-trustlens-runtime@${PROJECT_ID}.iam.gserviceaccount.com}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:latest"

 gcloud config set project "${PROJECT_ID}"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com

gcloud artifacts repositories describe "${REPOSITORY}" \
  --location="${REGION}" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="TrustLens container images"

if ! gcloud iam service-accounts describe "${RUNTIME_SA}" >/dev/null 2>&1; then
  gcloud iam service-accounts create trustlens-runtime \
    --display-name="TrustLens Cloud Run runtime"
fi

# Least-privilege permission for Gemini calls through Vertex AI.
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/aiplatform.user" \
  --quiet

gcloud builds submit \
  --tag "${IMAGE}" \
  --timeout=20m \
  .

# Create a concrete manifest from the checked-in template.
sed \
  -e "s/PROJECT_ID/${PROJECT_ID}/g" \
  -e "s/REGION/${REGION}/g" \
  -e "s#${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:latest#${IMAGE}#g" \
  -e "s#${RUNTIME_SA}#${RUNTIME_SA}#g" \
  cloudrun-service.yaml > /tmp/trustlens-service.yaml

# --allow-unauthenticated is intentional for a public hackathon demo only.
# Remove it and grant roles/run.invoker to your authenticated frontend/service
# account for any non-demo deployment.
gcloud run services replace /tmp/trustlens-service.yaml \
  --region="${REGION}"

gcloud run services add-iam-policy-binding "${SERVICE}" \
  --region="${REGION}" \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --quiet

SERVICE_URL="$(gcloud run services describe "${SERVICE}" \
  --region="${REGION}" \
  --format='value(status.url)')"
printf '\nDeployed TrustLens API: %s\n' "${SERVICE_URL}"
printf 'Health check: %s/healthz\n' "${SERVICE_URL}"
printf 'OpenAPI docs: %s/docs\n' "${SERVICE_URL}"
