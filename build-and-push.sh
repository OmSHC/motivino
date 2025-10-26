#!/bin/bash

# Build and push Docker images to registry
echo "🚀 Building and pushing Docker images..."

# Set your Docker Hub username
DOCKER_USERNAME="your-dockerhub-username"
IMAGE_TAG="latest"

echo "📦 Building backend image..."
docker build -t $DOCKER_USERNAME/motivation-backend:$IMAGE_TAG .

echo "📦 Building frontend image..."
docker build -t $DOCKER_USERNAME/motivation-frontend:$IMAGE_TAG ./frontend

echo "🔐 Logging into Docker Hub..."
docker login

echo "📤 Pushing backend image..."
docker push $DOCKER_USERNAME/motivation-backend:$IMAGE_TAG

echo "📤 Pushing frontend image..."
docker push $DOCKER_USERNAME/motivation-frontend:$IMAGE_TAG

echo "✅ Images pushed successfully!"
echo ""
echo "🌐 Images available at:"
echo "   Backend: docker.io/$DOCKER_USERNAME/motivation-backend:$IMAGE_TAG"
echo "   Frontend: docker.io/$DOCKER_USERNAME/motivation-frontend:$IMAGE_TAG"