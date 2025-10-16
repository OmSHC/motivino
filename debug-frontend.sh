#!/bin/bash

echo "🔍 Frontend Build & Serving Diagnostic"
echo "====================================="

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Checking frontend build status..."

# 1. Check if frontend build volume exists
log "📁 Checking frontend build volume..."
if docker volume ls | grep -q frontend_build; then
    log "✅ Frontend build volume exists"
else
    log "❌ Frontend build volume does NOT exist"
fi

# 2. Check what's inside the volume
log "📄 Contents of frontend build volume:"
docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/ 2>/dev/null || log "   Volume empty or not accessible"

# 3. Check what's in nginx html directory
log "🌐 Contents of nginx html directory:"
docker-compose -f docker-compose.prod.yml exec -T nginx ls -la /usr/share/nginx/html/ 2>/dev/null || log "   Cannot access nginx html directory"

# 4. Check frontend container logs
log "🏗️ Frontend container build logs (last 15 lines):"
docker-compose -f docker-compose.prod.yml logs frontend 2>/dev/null | tail -15 || log "   No frontend logs available"

# 5. Check if frontend container is still running
log "🐳 Frontend container status:"
docker-compose -f docker-compose.prod.yml ps frontend --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || log "   Cannot check frontend status"

# 6. Test direct nginx responses
log "🌐 Testing nginx static file serving:"
# Test index.html
if curl -s -I http://localhost/index.html 2>/dev/null | grep -q "200\|404"; then
    log "   ✅ index.html endpoint responds"
    curl -s http://localhost/index.html | head -3
else
    log "   ❌ index.html endpoint not responding"
fi

# Test static JS file
if curl -s -I http://localhost/static/js/main.*.js 2>/dev/null | grep -q "200\|404"; then
    log "   ✅ Static JS endpoint responds"
else
    log "   ❌ Static JS endpoint not responding"
fi

# 7. Check nginx configuration for static files
log "⚙️ Nginx static file configuration check:"
docker-compose -f docker-compose.prod.yml exec -T nginx grep -A 10 "location.*static" /etc/nginx/nginx.conf 2>/dev/null || log "   Cannot check nginx config"

echo ""
log "🎯 ANALYSIS & RECOMMENDATIONS:"
echo "=============================="

# Check if files exist in volume
VOLUME_HAS_FILES=$(docker run --rm -v motivino_frontend_build:/build alpine ls /build/index.html 2>/dev/null && echo "yes" || echo "no")

# Check if nginx can serve files
NGINX_CAN_SERVE=$(curl -s http://localhost/index.html 2>/dev/null | grep -q "doctype html" && echo "yes" || echo "no")

if [ "$VOLUME_HAS_FILES" = "no" ]; then
    log "❌ CRITICAL: No build files in volume"
    log "   💡 SOLUTION: Frontend build failed or didn't copy files"
    log "   💡 Try: docker-compose -f docker-compose.prod.yml up --build frontend"
elif [ "$NGINX_CAN_SERVE" = "no" ]; then
    log "❌ CRITICAL: Nginx cannot serve files"
    log "   💡 SOLUTION: Volume not mounted correctly or nginx config issue"
    log "   💡 Try: docker-compose -f docker-compose.prod.yml restart nginx"
else
    log "✅ Frontend files exist and are being served"
    log "❓ BROWSER: If browser shows 404, check network/firewall"
fi

log ""
log "🔧 QUICK FIXES TO TRY:"
log "======================"
log "1. Rebuild frontend: docker-compose -f docker-compose.prod.yml up --build frontend"
log "2. Restart nginx: docker-compose -f docker-compose.prod.yml restart nginx"
log "3. Check logs: docker-compose -f docker-compose.prod.yml logs frontend"
log "4. Clean rebuild: docker-compose -f docker-compose.prod.yml down -v && docker-compose -f docker-compose.prod.yml up -d"

log ""
log "📄 Provide this output if the issue persists!"
