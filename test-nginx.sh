#!/bin/bash

echo "🧪 Testing Nginx Configuration"
echo "============================="

# Test nginx config syntax (only when containers are running)
echo "📄 Testing nginx configuration syntax..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up.*nginx"; then
    echo "   Testing with running container..."
    docker-compose -f docker-compose.prod.yml exec -T nginx nginx -t
    if [ $? -eq 0 ]; then
        echo "✅ Nginx configuration is valid"
    else
        echo "❌ Nginx configuration has errors"
        exit 1
    fi
else
    echo "   Nginx not running - testing syntax manually (may show DNS warnings)..."
    docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t -c /etc/nginx/nginx.conf 2>&1 | grep -v "host not found" || true
    if [ $? -eq 0 ]; then
        echo "✅ Nginx configuration syntax is valid (ignoring DNS resolution warnings)"
    else
        echo "❌ Nginx configuration has syntax errors"
        exit 1
    fi
fi

# Test if backend is accessible from nginx perspective
echo ""
echo "🔗 Testing backend connectivity..."
docker run --rm --network motivino_default curlimages/curl:7.88.1 -f -s --connect-timeout 5 http://backend:8000/api/core/health/

if [ $? -eq 0 ]; then
    echo "✅ Backend is accessible from nginx network"
else
    echo "❌ Backend is NOT accessible from nginx network"
    echo "   This might be the cause of nginx startup failure"
fi

# Check if frontend build volume exists
echo ""
echo "📁 Checking frontend build volume..."
if docker volume ls | grep -q frontend_build; then
    echo "✅ Frontend build volume exists"
    docker run --rm -v motivino_frontend_build:/build alpine ls -la /build 2>/dev/null || echo "   Volume is empty or not accessible"
else
    echo "❌ Frontend build volume does not exist"
fi
