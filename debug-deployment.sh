#!/bin/bash

echo "🔍 GCP Deployment Diagnostic Tool"
echo "================================="

set -e

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "🔍 Starting comprehensive deployment diagnostics..."

# 1. Check if Docker is running
log "🐳 Checking Docker status..."
if ! docker info >/dev/null 2>&1; then
    log "❌ Docker is not running or not accessible"
    exit 1
else
    log "✅ Docker is running"
fi

# 2. Check Docker Compose services
log "📊 Checking Docker Compose services..."
if [ -f "docker-compose.prod.yml" ]; then
    log "📋 Current service status:"
    docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

    log "📋 Detailed container information:"
    docker-compose -f docker-compose.prod.yml ps -a
else
    log "❌ docker-compose.prod.yml not found"
    exit 1
fi

# 3. Check nginx container specifically
log "🌐 Checking Nginx container..."
NGINX_STATUS=$(docker-compose -f docker-compose.prod.yml ps nginx --format "{{.Status}}" 2>/dev/null || echo "not running")
if [[ $NGINX_STATUS == *"Up"* ]]; then
    log "✅ Nginx container is running"

    # Check nginx logs
    log "📄 Last 20 lines of nginx logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20 nginx

    # Check if nginx is listening on port 80
    log "🔍 Checking if nginx is listening on port 80..."
    if docker-compose -f docker-compose.prod.yml exec -T nginx netstat -tlnp 2>/dev/null | grep -q ":80 "; then
        log "✅ Nginx is listening on port 80 inside container"
    else
        log "❌ Nginx is NOT listening on port 80 inside container"
        docker-compose -f docker-compose.prod.yml exec -T nginx netstat -tlnp 2>/dev/null || log "   Could not check netstat"
    fi
else
    log "❌ Nginx container is NOT running"
    log "   Status: $NGINX_STATUS"
fi

# 4. Check backend container
log "🔧 Checking Backend container..."
BACKEND_STATUS=$(docker-compose -f docker-compose.prod.yml ps backend --format "{{.Status}}" 2>/dev/null || echo "not running")
if [[ $BACKEND_STATUS == *"Up"* ]]; then
    log "✅ Backend container is running"

    # Check backend health
    log "🏥 Testing backend health endpoint..."
    if docker-compose -f docker-compose.prod.yml exec -T backend curl -f -s http://localhost:8000/api/core/health/ >/dev/null 2>&1; then
        log "✅ Backend health check passed"
    else
        log "❌ Backend health check failed"
        log "📄 Backend logs (last 10 lines):"
        docker-compose -f docker-compose.prod.yml logs --tail=10 backend
    fi
else
    log "❌ Backend container is NOT running"
    log "   Status: $BACKEND_STATUS"
fi

# 5. Check port mapping
log "🔌 Checking port mappings..."
docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Ports}}"

# 6. Test local connectivity
log "🌐 Testing local connectivity..."
if curl -f -s --connect-timeout 5 http://localhost/health/ >/dev/null 2>&1; then
    log "✅ Local nginx health check passed"
else
    log "❌ Local nginx health check failed"
    # Try to curl with more verbose output
    log "🔍 Detailed curl test:"
    curl -v --connect-timeout 5 http://localhost/health/ 2>&1 | head -10
fi

# 7. Check system ports
log "🔍 Checking system port 80..."
if sudo netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    log "✅ Port 80 is in use on host system"
    sudo netstat -tlnp | grep ":80 "
else
    log "❌ Port 80 is NOT in use on host system"
fi

# 8. Check GCP firewall (if gcloud is available)
log "🔥 Checking GCP firewall rules..."
if command -v gcloud >/dev/null 2>&1; then
    log "   GCP firewall rules for port 80:"
    gcloud compute firewall-rules list --filter="allowed[].ports:(80)" --format="table(name,network,direction,allowed[].ports,sourceRanges)" 2>/dev/null || log "   Could not check GCP firewall"
else
    log "   gcloud CLI not available - cannot check GCP firewall"
fi

# 9. Network diagnostics
log "📡 Network diagnostics..."
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
log "   External IP: $EXTERNAL_IP"
log "   Internal hostname: $(hostname)"
log "   Internal IP: $(hostname -I 2>/dev/null || echo 'unknown')"

# 10. Docker network inspection
log "🌐 Docker network information..."
docker network ls | grep motivino || log "   motivino network not found"
docker network inspect motivino_default 2>/dev/null | grep -A 5 -B 5 "Containers" || log "   Could not inspect network"

log ""
log "🎯 SUMMARY & RECOMMENDATIONS:"
log "=============================="

# Analyze results and provide recommendations
NGINX_RUNNING=$(docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up" && echo "yes" || echo "no")
BACKEND_RUNNING=$(docker-compose -f docker-compose.prod.yml ps backend | grep -q "Up" && echo "yes" || echo "no")
PORT_80_USED=$(sudo netstat -tlnp 2>/dev/null | grep -q ":80 " && echo "yes" || echo "no")

if [ "$NGINX_RUNNING" = "no" ]; then
    log "❌ ISSUE: Nginx container is not running"
    log "   SOLUTION: Check nginx logs and restart: docker-compose -f docker-compose.prod.yml logs nginx"
elif [ "$PORT_80_USED" = "no" ]; then
    log "❌ ISSUE: Port 80 is not being used on the host"
    log "   SOLUTION: Nginx may not be binding correctly. Check container logs."
else
    log "✅ BASIC: Nginx is running and port 80 is in use"
    if curl -f -s http://localhost/health/ >/dev/null 2>&1; then
        log "✅ LOCAL: Nginx is responding locally"
        log "❓ REMOTE: If browser can't connect, check GCP firewall rules"
        log "   SOLUTION: Ensure firewall allows TCP:80 from 0.0.0.0/0"
    else
        log "❌ LOCAL: Nginx is not responding to local requests"
        log "   SOLUTION: Check nginx configuration and backend connectivity"
    fi
fi

log ""
log "🔧 QUICK FIXES TO TRY:"
log "======================"
log "1. Restart services: docker-compose -f docker-compose.prod.yml restart"
log "2. Rebuild and restart: docker-compose -f docker-compose.prod.yml up --build -d"
log "3. Check firewall: gcloud compute firewall-rules create allow-http --allow tcp:80 --source-ranges 0.0.0.0/0"
log "4. Test manually: curl http://localhost/health/"
log ""
log "📄 Provide the output above if you need further assistance!"
