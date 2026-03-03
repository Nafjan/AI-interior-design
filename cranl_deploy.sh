#!/bin/bash
# Deployment script for CranL
# Usage: REPO_ID=xxx ./cranl_deploy.sh

set -e

echo "Ensure you have connected GitHub: cranl github connect"

REPO_ID="${REPO_ID:?Set REPO_ID from 'cranl github repos'}"

echo "=== Deploying Backend ==="
cranl apps create --repo $REPO_ID --name ai-styling-backend --build-type nixpacks --branch main

# Inject Postgres + Redis
cranl db create --name ai-styling-db --type pg --inject ai-styling-backend
cranl db create --name ai-styling-redis --type redis --inject ai-styling-backend

# GCP Cloud Storage (uses Application Default Credentials or service account key)
cranl apps env set ai-styling-backend GCP_PROJECT_ID=gulfboost-odoo-login
cranl apps env set ai-styling-backend GCS_BUCKET=ai-home-styling-poc

# AI API keys
cranl apps env set ai-styling-backend OPENROUTER_API_KEY=$OPENROUTER_API_KEY
cranl apps env set ai-styling-backend GOOGLE_CLOUD_API_KEY=$GOOGLE_CLOUD_API_KEY

# App URLs
cranl apps env set ai-styling-backend API_URL=https://ai-styling-backend.cranl.app
cranl apps env set ai-styling-backend FRONTEND_URL=https://ai-styling-frontend.cranl.app

echo "=== Deploying Frontend ==="
cranl apps create --repo $REPO_ID --name ai-styling-frontend --build-type nixpacks --branch main
cranl apps env set ai-styling-frontend NEXT_PUBLIC_API_URL=https://ai-styling-backend.cranl.app

echo "=== Triggering Builds ==="
cranl apps deploy ai-styling-backend
cranl apps deploy ai-styling-frontend

echo "Done! Backend: https://ai-styling-backend.cranl.app"
echo "       Frontend: https://ai-styling-frontend.cranl.app"
