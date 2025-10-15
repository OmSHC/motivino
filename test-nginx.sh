#!/bin/bash

echo "🧪 Testing Nginx Configuration"
echo "============================="

# Test nginx config syntax
echo "📄 Testing nginx configuration syntax..."
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t -c /etc/nginx/nginx.conf

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
    exit 1
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
