#!/usr/bin/env bash
# Deploys snoonu-mcp-server to Cloud Run, $0 extra GCP services: Postgres and
# Redis run as sidecar containers in the same Cloud Run service instead of
# Cloud SQL / Memorystore. See deploy/gcloud/service.yaml.tpl for the trade-offs
# that come with that (single instance, non-persistent Postgres).
set -euo pipefail

# ---- config ----------------------------------------------------------------
PROJECT_ID="${PROJECT_ID:-snoonu-500713}"
PROJECT_NUMBER="${PROJECT_NUMBER:-1006350847085}"
REGION="${REGION:-me-central1}"
SERVICE_NAME="${SERVICE_NAME:-snoonu-mcp-server}"
REPO_NAME="${REPO_NAME:-snoonu-mcp-images}"          # separate from hala-images
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"
PG_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}-pg-seed:latest"

cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

# ---- 1. one-time setup (free) ----------------------------------------------
setup() {
  gcloud config set project "$PROJECT_ID"
  gcloud services enable run.googleapis.com artifactregistry.googleapis.com

  gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker --location="$REGION" \
    --description="snoonu-mcp-server images" || echo "repo already exists, continuing"

  gcloud auth configure-docker "${REGION}-docker.pkg.dev"
}

# ---- 2. build & push both images (free beyond Artifact Registry storage, cents) --
build_and_push() {
  docker build -t "$IMAGE" .
  docker push "$IMAGE"

  docker build -t "$PG_IMAGE" deploy/gcloud/db
  docker push "$PG_IMAGE"
}

# ---- 3. deploy to Cloud Run (free at low traffic: Cloud Run's always-free tier
#         covers ~2M requests/mo; this stays within it for dev/demo use) -------
deploy() {
  EXISTING_HOST="$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" \
    --format='value(status.url)' 2>/dev/null | sed 's#https://##' || true)"

  export PROJECT_ID PROJECT_NUMBER REGION SERVICE_NAME IMAGE PG_IMAGE EXISTING_HOST
  envsubst < deploy/gcloud/service.yaml.tpl > /tmp/snoonu-mcp-service.yaml

  gcloud run services replace /tmp/snoonu-mcp-service.yaml --region="$REGION"

  # Private by default (no --allow-unauthenticated equivalent in `services replace`).
  # Grant yourself invoker access to test:
  CALLER="$(gcloud config get-value account)"
  gcloud run services add-iam-policy-binding "$SERVICE_NAME" --region="$REGION" \
    --member="user:${CALLER}" --role="roles/run.invoker"

  echo "Service URL: $(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)')"
  echo "Test with: curl -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\" <url>/health"
}

# ---- to refresh the baked-in catalog data later -----------------------------
# docker exec snoonu-mcp-server-snoonu-db-1 pg_dump -U snoonu --data-only --inserts \
#   -t categories -t products -t cities snoonu_mcp > deploy/gcloud/db/02-seed-data.sql

"$@"
