# 🚀 Google Cloud Platform Deployment Guide

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed and authenticated
3. **Docker** installed on your local machine
4. **Domain name** (optional, for custom domain)

## Step 1: Setup GCP Project

```bash
# Set your project ID
PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 2: Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env.prod
nano .env.prod

# Edit with your production settings:
# SECRET_KEY=your-generated-secret-key
# DATABASE_PASSWORD=your-secure-password
# DOMAIN=your-domain.com
# OPENAI_API_KEY=your-openai-key
```

## Step 3: Deploy with Script

```bash
# Run the deployment script
./gcp-deploy.sh
```

## Step 4: Manual Deployment (Alternative)

### Build and Push Images

```bash
# Authenticate Docker
gcloud auth configure-docker

# Build backend image
docker build -t gcr.io/$PROJECT_ID/motivation-backend:latest .

# Build frontend image
docker build -t gcr.io/$PROJECT_ID/motivation-frontend:latest ./frontend

# Push images
docker push gcr.io/$PROJECT_ID/motivation-backend:latest
docker push gcr.io/$PROJECT_ID/motivation-frontend:latest
```

### Setup Database (Cloud SQL)

```bash
# Create PostgreSQL instance
gcloud sql instances create motivation-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database and user
gcloud sql databases create motivation_news --instance=motivation-db
gcloud sql users create motivation_user \
    --instance=motivation-db \
    --password=your-secure-password
```

### Setup Redis (Memorystore)

```bash
# Create Redis instance
gcloud redis instances create motivation-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7
```

### Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy motivation-backend \
    --image gcr.io/$PROJECT_ID/motivation-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DEBUG=False,SECRET_KEY=your-secret,DATABASE_ENGINE=django.db.backends.postgresql,DATABASE_NAME=motivation_news,DATABASE_USER=motivation_user,DATABASE_PASSWORD=your-password,DATABASE_HOST=/cloudsql/$PROJECT_ID:us-central1:motivation-db,REDIS_URL=redis://10.0.0.1:6379/0

# Deploy frontend
gcloud run deploy motivation-frontend \
    --image gcr.io/$PROJECT_ID/motivation-frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars REACT_APP_API_URL=https://motivation-backend-123456.us-central1.run.app/api
```

## Step 5: Domain Setup (Optional)

### Option A: Google Load Balancer

```bash
# Create load balancer
gcloud compute addresses create motivation-lb-ip --global

# Create SSL certificate
gcloud compute ssl-certificates create motivation-ssl \
    --domains=your-domain.com

# Create backend services
gcloud compute backend-services create motivation-backend-service \
    --protocol=HTTP \
    --global

gcloud compute backend-services add-backend motivation-backend-service \
    --instance-group=motivation-frontend \
    --global

# Create URL map
gcloud compute url-maps create motivation-url-map \
    --default-service=motivation-backend-service

# Create HTTPS proxy
gcloud compute target-https-proxies create motivation-https-proxy \
    --ssl-certificates=motivation-ssl \
    --url-map=motivation-url-map
```

### Option B: Custom Domain

```bash
# Point your domain to the load balancer IP
# Update DNS A record to point to the load balancer IP
```

## Step 6: Production URLs

After deployment:

- **Frontend**: https://your-domain.com
- **Backend API**: https://motivation-backend-123456.us-central1.run.app/api
- **Admin**: https://your-domain.com/admin

## Step 7: Environment Variables

Update your `.env.prod` file with:

```bash
# Production settings
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (Cloud SQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=motivation_news
DATABASE_USER=motivation_user
DATABASE_PASSWORD=your-database-password
DATABASE_HOST=/cloudsql/your-project:us-central1:motivation-db

# Redis
REDIS_URL=redis://10.0.0.1:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Domain
DOMAIN=your-domain.com
```

## Monitoring and Maintenance

### View Logs
```bash
# Backend logs
gcloud run services logs read motivation-backend --region us-central1

# Frontend logs
gcloud run services logs read motivation-frontend --region us-central1
```

### Update Deployment
```bash
# Rebuild and redeploy
docker build -t gcr.io/$PROJECT_ID/motivation-backend:latest .
docker push gcr.io/$PROJECT_ID/motivation-backend:latest
gcloud run services update motivation-backend --image gcr.io/$PROJECT_ID/motivation-backend:latest
```

### Database Backup
```bash
# Create backup
gcloud sql backups create --instance=motivation-db

# List backups
gcloud sql backups list --instance=motivation-db
```

## Security Considerations

1. **Secret Management**: Use Google Secret Manager for sensitive data
2. **HTTPS Only**: Force HTTPS in production
3. **CORS Configuration**: Restrict origins to your domain only
4. **Database Security**: Use strong passwords and proper firewall rules
5. **API Keys**: Store OpenAI keys securely

## Cost Optimization

- **Cloud SQL**: Start with db-f1-micro, scale as needed
- **Memorystore**: Basic tier for development
- **Cloud Run**: Pay only for usage
- **Load Balancer**: Only needed for custom domains

## Troubleshooting

### Common Issues:

1. **Database Connection**: Check Cloud SQL instance status and firewall
2. **Image Pull**: Ensure images are pushed to GCR
3. **Environment Variables**: Verify all required env vars are set
4. **DNS**: Check domain propagation (can take up to 48 hours)

### Debug Commands:

```bash
# Check service status
gcloud run services describe motivation-backend --region us-central1

# View logs
gcloud run services logs read motivation-backend --region us-central1 --limit=50

# Check database connectivity
gcloud sql connect motivation-db --user=motivation_user
```

## Production Checklist

- [ ] Domain configured and SSL certificate installed
- [ ] Database backups scheduled
- [ ] Monitoring and alerting set up
- [ ] Environment variables secured
- [ ] Static files properly served
- [ ] Health checks configured
- [ ] Load balancer configured (if using custom domain)
- [ ] Database user with minimal permissions
- [ ] Regular security updates

## Support

For issues with Google Cloud Platform:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Memorystore Documentation](https://cloud.google.com/memorystore/docs)
