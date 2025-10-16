#!/bin/bash

echo "🔍 COMPLETE GCP DEPLOYMENT DIAGNOSTIC"
echo "====================================="
echo ""

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting comprehensive diagnostic..."

# 1. System Information
echo "🖥️  SYSTEM INFORMATION:"
echo "======================"
log "OS: $(uname -a)"
log "Docker version: $(docker --version 2>/dev/null || echo 'Docker not available')"
log "Docker Compose version: $(docker-compose --version 2>/dev/null || echo 'Docker Compose not available')"
log "External IP: $(curl -s ifconfig.me 2>/dev/null || echo 'Unable to get IP')"
log "Internal IP: $(hostname -I 2>/dev/null | awk '{print $1}' || echo 'Unable to get IP')"
echo ""

# 2. GCP Firewall Check
echo "🔥 GCP FIREWALL CHECK:"
echo "======================"
if command -v gcloud >/dev/null 2>&1; then
    log "GCP CLI available - checking firewall rules..."
    echo "Current firewall rules for port 80:"
    gcloud compute firewall-rules list --filter="allowed[].ports:(80)" --format="table(name,network,direction,allowed[].ports,sourceRanges)" 2>/dev/null || log "Unable to check GCP firewall"
else
    log "GCP CLI not available - cannot check firewall rules"
    log "To check firewall manually: gcloud compute firewall-rules list --filter='allowed[].ports:(80)'"
fi
echo ""

# 3. Docker Status
echo "🐳 DOCKER STATUS:"
echo "================="
log "Docker info:"
docker info 2>/dev/null | grep -E "(Containers|Images|Server Version)" | head -5 || log "Docker not accessible"

log "Docker images:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "(REPOSITORY|motivation)" || log "No motivation images found"

log "Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || log "No running containers"
echo ""

# 4. Docker Compose Status
echo "📊 DOCKER COMPOSE STATUS:"
echo "========================="
if [ -f "docker-compose.prod.yml" ]; then
    log "Docker Compose file exists"
    log "Service status:"
    docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || log "Unable to get compose status"

    log "Detailed container status:"
    docker-compose -f docker-compose.prod.yml ps -a 2>/dev/null || log "Unable to get detailed status"
else
    log "❌ docker-compose.prod.yml not found"
fi
echo ""

# 5. Port Analysis
echo "🔌 PORT ANALYSIS:"
echo "================="
log "Processes using port 80:"
sudo netstat -tlnp 2>/dev/null | grep ":80 " || log "No processes using port 80"

log "Docker port mappings:"
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -v "NAMES" || log "No port mappings"
echo ""

# 6. Nginx Specific Checks
echo "🌐 NGINX SPECIFIC CHECKS:"
echo "========================="
if docker-compose -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -q "Up"; then
    log "✅ Nginx container is running"

    log "Nginx logs (last 10 lines):"
    docker-compose -f docker-compose.prod.yml logs --tail=10 nginx 2>/dev/null

    log "Testing nginx configuration:"
    docker-compose -f docker-compose.prod.yml exec -T nginx nginx -t 2>/dev/null || log "Cannot test nginx config"

    log "Nginx processes:"
    docker-compose -f docker-compose.prod.yml exec -T nginx ps aux | grep nginx 2>/dev/null || log "Cannot check nginx processes"

    log "Nginx listening ports:"
    docker-compose -f docker-compose.prod.yml exec -T nginx netstat -tlnp 2>/dev/null | grep -E ":(80|443)" || log "Nginx not listening on expected ports"

else
    log "❌ Nginx container is NOT running"

    log "Attempting to start nginx manually to see error:"
    docker-compose -f docker-compose.prod.yml up -d nginx 2>&1

    log "Checking nginx startup logs:"
    docker-compose -f docker-compose.prod.yml logs nginx 2>/dev/null | tail -10

    log "Nginx container status:"
    docker ps -a --filter "name=nginx" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi
echo ""

# 7. Backend Checks
echo "🔧 BACKEND CHECKS:"
echo "=================="
if docker-compose -f docker-compose.prod.yml ps backend 2>/dev/null | grep -q "Up"; then
    log "✅ Backend container is running"

    log "Backend health check:"
    docker-compose -f docker-compose.prod.yml exec -T backend curl -f -s --connect-timeout 5 http://localhost:8000/api/core/health/ 2>/dev/null && log "✅ Backend health check passed" || log "❌ Backend health check failed"

    log "Backend logs (last 5 lines):"
    docker-compose -f docker-compose.prod.yml logs --tail=5 backend 2>/dev/null
else
    log "❌ Backend container is NOT running"
fi
echo ""

# 8. Frontend Build Check
echo "⚛️  FRONTEND BUILD CHECK:"
echo "========================"
log "Checking frontend build volume:"
docker volume ls | grep frontend_build && log "✅ Frontend build volume exists" || log "❌ Frontend build volume missing"

if docker volume ls | grep -q frontend_build; then
    log "Contents of frontend build volume:"
    docker run --rm -v motivino_frontend_build:/build alpine ls -la /build 2>/dev/null || log "Volume empty or not accessible"
fi
echo ""

# 9. Network Tests
echo "🌐 NETWORK TESTS:"
echo "================="
log "Testing local connectivity:"

# Test nginx
if curl -f -s --connect-timeout 5 --max-time 10 http://localhost/health/ >/dev/null 2>&1; then
    log "✅ Local nginx health check: PASSED"
else
    log "❌ Local nginx health check: FAILED"
    curl -v --connect-timeout 5 --max-time 10 http://localhost/health/ 2>&1 | head -5
fi

# Test backend API
if curl -f -s --connect-timeout 5 --max-time 10 http://localhost/api/core/health/ >/dev/null 2>&1; then
    log "✅ Local backend API: PASSED"
else
    log "❌ Local backend API: FAILED"
fi

# Test frontend static files
if curl -f -s --connect-timeout 5 --max-time 10 -I http://localhost/index.html >/dev/null 2>&1; then
    log "✅ Local frontend: PASSED"
else
    log "❌ Local frontend: FAILED"
fi
echo ""

# 10. Configuration Validation
echo "⚙️  CONFIGURATION VALIDATION:"
echo "=============================="
if [ -f "nginx.conf" ]; then
    log "✅ nginx.conf exists"

    log "Testing nginx configuration:"
    if [ -f "test-nginx.sh" ]; then
        ./test-nginx.sh 2>/dev/null | grep -E "(✅|❌)" | while read line; do log "   $line"; done
    else
        log "   test-nginx.sh not found, using basic syntax check"
        docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t -c /etc/nginx/nginx.conf 2>&1 && log "   ✅ Nginx config syntax: VALID" || log "   ❌ Nginx config syntax: INVALID"
    fi
else
    log "❌ nginx.conf not found"
fi

if [ -f "docker-compose.prod.yml" ]; then
    log "✅ docker-compose.prod.yml exists"

    log "Validating docker-compose syntax:"
    docker-compose -f docker-compose.prod.yml config --quiet 2>&1 && log "✅ Docker Compose config: VALID" || log "❌ Docker Compose config: INVALID"
else
    log "❌ docker-compose.prod.yml not found"
fi
echo ""

# 11. Resource Usage
echo "📈 RESOURCE USAGE:"
echo "=================="
log "Docker system usage:"
docker system df 2>/dev/null || log "Cannot get docker usage"

log "Container resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || log "Cannot get container stats"
echo ""

# 12. Recommendations
echo "🎯 RECOMMENDATIONS:"
echo "=================="

# Analyze results and provide recommendations
NGINX_RUNNING=$(docker-compose -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -q "Up" && echo "yes" || echo "no")
BACKEND_RUNNING=$(docker-compose -f docker-compose.prod.yml ps backend 2>/dev/null | grep -q "Up" && echo "yes" || echo "no")
PORT_80_USED=$(sudo netstat -tlnp 2>/dev/null | grep -q ":80 " && echo "yes" || echo "no")
LOCAL_NGINX_WORKS=$(curl -f -s --connect-timeout 5 http://localhost/health/ >/dev/null 2>&1 && echo "yes" || echo "no")

if [ "$NGINX_RUNNING" = "no" ]; then
    log "🚨 CRITICAL: Nginx container is not running"
    log "   💡 SOLUTION: Check nginx logs above and fix configuration errors"
    log "   💡 Try: docker-compose -f docker-compose.prod.yml logs nginx"
elif [ "$PORT_80_USED" = "no" ]; then
    log "🚨 CRITICAL: Nothing is listening on port 80"
    log "   💡 SOLUTION: Nginx container may be failing to bind to port 80"
    log "   💡 Check: docker-compose -f docker-compose.prod.yml ps"
elif [ "$LOCAL_NGINX_WORKS" = "no" ]; then
    log "🚨 CRITICAL: Nginx is running but not responding to requests"
    log "   💡 SOLUTION: Check nginx configuration and backend connectivity"
    log "   💡 Try: docker-compose -f docker-compose.prod.yml exec nginx nginx -t"
else
    log "✅ BASIC: Services appear to be running locally"
    log "❓ REMOTE: If browser can't connect, check GCP firewall"
    log "   💡 SOLUTION: Ensure firewall allows TCP:80 from 0.0.0.0/0"
fi

log ""
log "🔧 QUICK FIXES TO TRY:"
log "======================"
log "1. Restart all services: docker-compose -f docker-compose.prod.yml restart"
log "2. Rebuild and redeploy: docker-compose -f docker-compose.prod.yml up --build -d"
log "3. Check firewall: gcloud compute firewall-rules create allow-http --allow tcp:80 --source-ranges 0.0.0.0/0 --description 'Allow HTTP'"
log "4. Clean restart: docker-compose -f docker-compose.prod.yml down && ./gcp-production-deploy.sh"
log "5. Manual nginx test: docker run -p 80:80 -v \$(pwd)/nginx.conf:/etc/nginx/nginx.conf nginx:alpine"

log ""
log "📄 SHARE THIS OUTPUT if you need further assistance!"
log ""
log "Diagnostic completed at: $(date)"
