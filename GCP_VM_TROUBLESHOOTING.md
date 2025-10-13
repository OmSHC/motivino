# 🚨 GCP VM Docker Troubleshooting Guide

## Issue: Docker Permission Denied

### Root Cause
Docker daemon socket requires root privileges or user needs to be in docker group.

### Solution 1: Add User to Docker Group (Recommended)

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again (important!)
exit
# SSH back in
gcloud compute ssh your-vm-instance --zone=your-zone

# Test Docker
docker --version
```

### Solution 2: Use Sudo with Docker Commands

```bash
# Use sudo with all docker commands
sudo docker-compose -f docker-compose.prod.yml ps
sudo docker-compose -f docker-compose.prod.yml logs -f
sudo docker-compose -f docker-compose.prod.yml down
```

## Issue: Docker Daemon Not Running

### Check Docker Status
```bash
sudo systemctl status docker
```

### Start Docker Service
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

## Issue: Port Already in Use

### Check what's using the port
```bash
sudo lsof -i :8001
sudo lsof -i :3000
```

### Kill processes using the ports
```bash
sudo kill -9 <PID>
```

## Issue: Database Connection Failed

### Check if database container is running
```bash
sudo docker-compose -f docker-compose.prod.yml ps
```

### Check database logs
```bash
sudo docker-compose -f docker-compose.prod.yml logs db
```

### Check database connectivity
```bash
sudo docker-compose -f docker-compose.prod.yml exec db pg_isready -U motivation_user
```

## Issue: Migration Errors

### Check if migrations need to be applied
```bash
sudo docker-compose -f docker-compose.prod.yml exec backend python manage.py showmigrations
```

### Apply migrations manually
```bash
sudo docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## Issue: Static Files Not Loading

### Collect static files manually
```bash
sudo docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### Check nginx configuration
```bash
sudo docker-compose -f docker-compose.prod.yml logs nginx
```

## Issue: Environment Variables Not Working

### Check if .env file exists
```bash
ls -la .env*
```

### Check environment variables in container
```bash
sudo docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE
```

## Issue: Memory Issues

### Check available memory
```bash
free -h
```

### Check Docker resource usage
```bash
sudo docker system df
```

## Issue: Network Issues

### Check firewall rules
```bash
sudo ufw status
```

### Allow HTTP/HTTPS traffic
```bash
sudo ufw allow 80
sudo ufw allow 443
```

## Issue: SSL Certificate Issues

### Check SSL certificate status
```bash
sudo docker-compose -f docker-compose.prod.yml logs nginx | grep -i ssl
```

### Regenerate SSL certificate
```bash
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up --build -d
```

## Quick Fix Commands

### Restart everything
```bash
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up --build -d
```

### Clean restart
```bash
sudo docker-compose -f docker-compose.prod.yml down
sudo docker system prune -f
sudo docker-compose -f docker-compose.prod.yml up --build -d
```

### Check all logs
```bash
sudo docker-compose -f docker-compose.prod.yml logs -f
```

## Production Checklist

- [ ] Docker daemon running
- [ ] User in docker group
- [ ] Ports 80, 443 open
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificate configured
- [ ] Environment variables set
- [ ] Services healthy
- [ ] Application accessible

## Getting Help

### Check service health
```bash
sudo docker-compose -f docker-compose.prod.yml ps
```

### View specific service logs
```bash
sudo docker-compose -f docker-compose.prod.yml logs backend
sudo docker-compose -f docker-compose.prod.yml logs frontend
sudo docker-compose -f docker-compose.prod.yml logs nginx
```

### Check database connectivity
```bash
sudo docker-compose -f docker-compose.prod.yml exec db pg_isready
```

### Check application health
```bash
curl http://localhost/health/
```
