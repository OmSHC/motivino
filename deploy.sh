#!/bin/bash

# Deployment script for Motivation News
echo "🚀 Deploying Motivation News..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

echo "📥 Pulling latest code..."
git pull origin main

echo "📦 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down

echo "🧹 Cleaning up old images..."
docker system prune -f

echo "📦 Building and starting services with fresh build..."
# Build with no cache to ensure latest changes are included
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating admin user..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_admin --email=admin@example.com --password=admin123 --first-name=Admin --last-name=User

echo "✅ Deployment completed!"
echo ""
echo "🌐 Services available at:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api"
echo "   Admin: http://localhost/admin"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
