#!/bin/bash
# Deployment script for CranL
# Usage: ./cranl_deploy.sh

set -e

echo "=== Pre-flight Checks ==="
if [ -f .env ]; then
  echo "Loading .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Validate essential env vars
if [[ -z "$DATABASE_URL" ]] || [[ "$DATABASE_URL" == *"localhost"* ]]; then
  echo "ERROR: DATABASE_URL is missing or points to localhost. It must be a production Postgres URL."
  exit 1
fi

if [[ -z "$REDIS_URL" ]] || [[ "$REDIS_URL" == *"localhost"* ]]; then
  echo "ERROR: REDIS_URL is missing or points to localhost. It must be a production Redis URL."
  exit 1
fi

if [[ -z "$OPENROUTER_API_KEY" ]]; then
  echo "ERROR: OPENROUTER_API_KEY is missing."
  exit 1
fi

# URLs mapped from CranL dashboard
CRANL_BACKEND_URL="https://ai-styling-backend-dkpiok.cranl.net"
CRANL_FRONTEND_URL="https://ai-styling-frontend-vljrz9.cranl.net"

REPO_ID="23bd2e35-51ff-48ba-9dff-85f0e35b7194" # gulfboost/AI-interior-design

echo "=== Deploying Backend ==="
# cranl apps create --repo $REPO_ID --name ai-styling-backend --build-type nixpacks --branch main --build-path api

cranl apps env set ai-styling-backend GCP_PROJECT_ID=gulfboost-odoo-login
cranl apps env set ai-styling-backend GCS_BUCKET=ai-home-styling-poc
cranl apps env set ai-styling-backend OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
cranl apps env set ai-styling-backend GOOGLE_CLOUD_API_KEY="$GOOGLE_CLOUD_API_KEY"
cranl apps env set ai-styling-backend API_URL="$CRANL_BACKEND_URL"
cranl apps env set ai-styling-backend FRONTEND_URL="$CRANL_FRONTEND_URL"
cranl apps env set ai-styling-backend DATABASE_URL="$DATABASE_URL"
cranl apps env set ai-styling-backend REDIS_URL="$REDIS_URL"
cranl apps env set ai-styling-backend APP_TYPE="backend"

echo "=== Deploying Worker ==="
# cranl apps create --repo $REPO_ID --name ai-styling-worker --build-type nixpacks --branch main --build-path api
# We'll use the same env vars for the worker
cranl apps env set ai-styling-worker GCP_PROJECT_ID=gulfboost-odoo-login
cranl apps env set ai-styling-worker GCS_BUCKET=ai-home-styling-poc
cranl apps env set ai-styling-worker OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
cranl apps env set ai-styling-worker GOOGLE_CLOUD_API_KEY="$GOOGLE_CLOUD_API_KEY"
cranl apps env set ai-styling-worker API_URL="$CRANL_BACKEND_URL"
cranl apps env set ai-styling-worker DATABASE_URL="$DATABASE_URL"
cranl apps env set ai-styling-worker REDIS_URL="$REDIS_URL"
cranl apps env set ai-styling-worker APP_TYPE="worker"

echo "=== Deploying Frontend ==="
# cranl apps create --repo $REPO_ID --name ai-styling-frontend --build-type nixpacks --branch main --build-path frontend
cranl apps env set ai-styling-frontend NEXT_PUBLIC_API_URL="$CRANL_BACKEND_URL"
cranl apps env set ai-styling-frontend APP_TYPE="frontend"

echo "=== Triggering Builds ==="
cranl apps deploy ai-styling-backend
# Worker deployment might need to be triggered after creation
# cranl apps deploy ai-styling-worker
cranl apps deploy ai-styling-frontend

echo "Done!"
echo "Backend: $CRANL_BACKEND_URL"
echo "Frontend: $CRANL_FRONTEND_URL"
