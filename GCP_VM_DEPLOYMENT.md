# 🚀 Google Cloud Platform VM Deployment Guide

## Step 1: Connect to Your GCP VM

```bash
# SSH into your GCP VM
gcloud compute ssh your-vm-instance-name --zone=your-zone
```

## Step 2: Install Required Software

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get install -y git

# Logout and login to apply Docker group changes
exit
# SSH back in
gcloud compute ssh your-vm-instance-name --zone=your-zone
```

## Step 3: Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/OmSHC/motivino.git
cd motivino

# Copy environment file
cp .env.example .env

# Edit environment file with your settings
nano .env
```

## Step 4: Configure Environment Variables

Edit `.env` with your production settings:

```bash
# Required settings
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (will be created automatically)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=motivation_news
DATABASE_USER=motivation_user
DATABASE_PASSWORD=your-secure-password
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Domain
DOMAIN=your-domain.com

# Optional
OPENAI_API_KEY=your-openai-key
```

## Step 5: Deploy with Docker

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to start (about 30 seconds)
sleep 30

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Create admin user
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_admin
```

## Step 6: Verify Deployment

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Test API
curl http://localhost:8001/api/
```

## Step 7: Set Up Domain (Optional)

### Option A: Update DNS
1. Get your VM's external IP: `curl -s ifconfig.me`
2. Update your DNS A record to point to this IP
3. Wait for DNS propagation (can take up to 48 hours)

### Option B: Use Google Load Balancer
```bash
# Create static IP
gcloud compute addresses create motivation-ip --global

# Create SSL certificate
gcloud compute ssl-certificates create motivation-cert \
    --domains=your-domain.com --global

# Create load balancer (more complex setup)
# Refer to GCP Load Balancer documentation
```

## Step 8: Access Your Application

After deployment:

- **Frontend:** http://your-vm-ip
- **Backend API:** http://your-vm-ip/api
- **Admin Panel:** http://your-vm-ip/admin

## Step 9: Production Security

```bash
# Update firewall rules to allow HTTP/HTTPS
gcloud compute firewall-rules create allow-http \
    --allow tcp:80,tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server

# Tag your VM
gcloud compute instances add-tags your-vm-instance --tags http-server
```

## Monitoring and Maintenance

### Useful Commands:

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# Update deployment
git pull
docker-compose -f docker-compose.prod.yml up --build -d
```

### Database Backup:
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U motivation_user motivation_news > backup.sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U motivation_user -d motivation_news < backup.sql
```

## Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Kill processes using ports
   sudo lsof -ti:8001 | xargs sudo kill -9
   sudo lsof -ti:3000 | xargs sudo kill -9
   ```

2. **Permission denied:**
   ```bash
   # Fix Docker permissions
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

3. **Database connection failed:**
   ```bash
   # Check database status
   docker-compose -f docker-compose.prod.yml exec db pg_isready -U motivation_user
   ```

4. **Build fails:**
   ```bash
   # Clean Docker
   docker system prune -f
   docker-compose -f docker-compose.prod.yml build --no-cache
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

For GCP-specific issues:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Memorystore Documentation](https://cloud.google.com/memorystore/docs)
- [Load Balancer Documentation](https://cloud.google.com/load-balancing/docs)

## Cost Monitoring

Monitor your GCP costs:
- [Cloud Console Billing](https://console.cloud.google.com/billing)
- Set up billing alerts for budget monitoring
- Use Cloud Monitoring for resource usage tracking
