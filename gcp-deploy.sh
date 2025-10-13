#!/bin/bash

# GCP Deployment Script for Motivation News
echo "🚀 Deploying to Google Cloud Platform..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not logged in to gcloud. Please run:"
    echo "   gcloud auth login"
    exit 1
fi

# Set your GCP project ID
PROJECT_ID="your-gcp-project-id"
echo "Using project: $PROJECT_ID"

# Create environment file for production
cat > .env.prod << EOF_ENV
# Production Environment Variables
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (Cloud SQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=motivation_news
DATABASE_USER=motivation_user
DATABASE_PASSWORD=$(openssl rand -base64 32)
DATABASE_HOST=/cloudsql/${PROJECT_ID}:us-central1:motivation-db
DATABASE_PORT=5432

# Redis (Memorystore)
REDIS_URL=redis://10.0.0.1:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Domain
DOMAIN=your-domain.com
EOF_ENV

echo "✅ Created .env.prod file"
echo "📝 Please edit .env.prod with your actual domain and settings"

# Build and push Docker images
echo "🐳 Building Docker images..."
docker build -t gcr.io/${PROJECT_ID}/motivation-backend:latest .
docker build -t gcr.io/${PROJECT_ID}/motivation-frontend:latest ./frontend

echo "📤 Pushing images to Google Container Registry..."
gcloud auth configure-docker --quiet
docker push gcr.io/${PROJECT_ID}/motivation-backend:latest
docker push gcr.io/${PROJECT_ID}/motivation-frontend:latest

echo "✅ Images pushed to GCR"

# Create Cloud SQL instance
echo "🗄️ Creating Cloud SQL instance..."
gcloud sql instances create motivation-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=$(openssl rand -base64 32)

# Create database and user
echo "🔧 Setting up database..."
gcloud sql databases create motivation_news --instance=motivation-db
gcloud sql users create motivation_user \
    --instance=motivation-db \
    --password=$(grep DATABASE_PASSWORD .env.prod | cut -d'=' -f2)

echo "✅ Database setup complete"

# Create Redis instance (Memorystore)
echo "⚡ Creating Redis instance..."
gcloud redis instances create motivation-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7

echo "✅ Redis setup complete"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."

# Deploy backend
gcloud run deploy motivation-backend \
    --image gcr.io/${PROJECT_ID}/motivation-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars $(cat .env.prod | grep -v '^#' | sed 's/^/"/' | sed 's/$/"/' | tr '\n' ',' | sed 's/,$//') \
    --set-cloudsql-instances ${PROJECT_ID}:us-central1:motivation-db \
    --set-env-vars REDIS_URL=redis://10.0.0.1:6379/0

# Deploy frontend
gcloud run deploy motivation-frontend \
    --image gcr.io/${PROJECT_ID}/motivation-frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars REACT_APP_API_URL=https://motivation-backend-123456789.us-central1.run.app/api

echo "✅ Services deployed to Cloud Run"

# Get service URLs
BACKEND_URL=$(gcloud run services describe motivation-backend --platform managed --region us-central1 --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe motivation-frontend --platform managed --region us-central1 --format="value(status.url)")

echo "�� Deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "   Backend API: $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Update DNS to point your-domain.com to the frontend URL"
echo "   2. Update .env.prod with correct domain and API URL"
echo "   3. Redeploy with updated environment variables"
echo "   4. Set up SSL certificate with Google Load Balancer"
