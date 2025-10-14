#!/bin/bash

set -e  # Exit on any error

echo "🏗️  Build and Push Docker Images to Registry"
echo "=========================================="

# Default registry
REGISTRY_URL=${REGISTRY_URL:-"gcr.io/your-project-id"}
TAG=${TAG:-"latest"}

echo "Registry: $REGISTRY_URL"
echo "Tag: $TAG"
echo ""

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Authenticate with registry (customize based on your registry)
if [[ $REGISTRY_URL == gcr.io/* ]]; then
    log "🔐 Authenticating with Google Container Registry..."
    gcloud auth configure-docker --quiet
elif [[ $REGISTRY_URL == *.azurecr.io ]]; then
    log "🔐 Authenticating with Azure Container Registry..."
    az acr login --name $(echo $REGISTRY_URL | cut -d'.' -f1)
else
    log "⚠️  Please ensure you're authenticated with: $REGISTRY_URL"
fi

# Build and push backend
log "🐳 Building and pushing backend image..."
docker build -t $REGISTRY_URL/motivation-backend:$TAG .
docker push $REGISTRY_URL/motivation-backend:$TAG

# Build and push frontend
log "⚛️  Building and pushing frontend image..."
cd frontend
docker build -t $REGISTRY_URL/motivation-frontend:$TAG .
docker push $REGISTRY_URL/motivation-frontend:$TAG
cd ..

log "✅ All images built and pushed successfully!"
echo ""
echo "📋 Images available:"
echo "   Backend: $REGISTRY_URL/motivation-backend:$TAG"
echo "   Frontend: $REGISTRY_URL/motivation-frontend:$TAG"
echo ""
echo "🚀 Deploy with:"
echo "   USE_REGISTRY=true REGISTRY_URL=$REGISTRY_URL ./gcp-production-deploy.sh"
