#!/bin/bash

# GCP Deployment script - pulls pre-built images
echo "🚀 Deploying to GCP with pre-built images..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Set your Docker Hub username and image tag
DOCKER_USERNAME=${DOCKER_USERNAME:-"your-dockerhub-username"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

echo "📥 Pulling latest images from registry..."
docker-compose -f docker-compose.gcp.yml pull

echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.gcp.yml down

echo "🧹 Cleaning up old images..."
docker system prune -f

echo "🚀 Starting services with pre-built images..."
docker-compose -f docker-compose.gcp.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.gcp.yml ps

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.gcp.yml exec backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.gcp.yml exec backend python manage.py collectstatic --noinput

echo "✅ Deployment completed!"
echo ""
echo "🌐 Services available at:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api"
echo "   Admin: http://localhost/admin"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.gcp.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.gcp.yml down"
echo "   Restart: docker-compose -f docker-compose.gcp.yml restart"
