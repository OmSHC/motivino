#!/bin/bash

echo "🔍 Checking Frontend Build Status"
echo "================================="

# Check if frontend build volume exists
echo "📁 Checking frontend build volume..."
docker volume ls | grep frontend_build

if docker volume ls | grep -q frontend_build; then
    echo "✅ Frontend build volume exists"

    # Check what's inside the volume
    echo ""
    echo "📄 Contents of frontend build volume:"
    docker run --rm -v motivino_frontend_build:/build alpine ls -la /build 2>/dev/null || echo "   Volume is empty or not accessible"

    # Try to list files if they exist
    echo ""
    echo "📋 Detailed file listing:"
    docker run --rm -v motivino_frontend_build:/build alpine find /build -type f 2>/dev/null | head -20 || echo "   No files found in volume"

    # Check if index.html exists
    echo ""
    echo "🔍 Checking for index.html:"
    docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/index.html 2>/dev/null || echo "   index.html not found"

    # Check if static files exist
    echo ""
    echo "🔍 Checking for static directory:"
    docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/static/ 2>/dev/null || echo "   static directory not found"

else
    echo "❌ Frontend build volume does not exist"
fi

# Check nginx html directory
echo ""
echo "🌐 Checking nginx html directory..."
docker-compose -f docker-compose.prod.yml exec -T nginx ls -la /usr/share/nginx/html 2>/dev/null || echo "   Cannot access nginx html directory"

# Check if nginx can serve the files
echo ""
echo "🔗 Testing nginx file serving..."
if curl -s -I http://localhost/index.html 2>/dev/null | grep -q "200\|404"; then
    echo "✅ Nginx can serve index.html"
    curl -s http://localhost/index.html | head -5
else
    echo "❌ Nginx cannot serve index.html"
fi

echo ""
echo "🎯 RECOMMENDATIONS:"
echo "=================="

if ! docker volume ls | grep -q frontend_build; then
    echo "❌ Fix: Frontend build volume missing - recreate containers"
    echo "   docker-compose -f docker-compose.prod.yml down -v"
    echo "   docker-compose -f docker-compose.prod.yml up --build frontend"
elif ! docker run --rm -v motivino_frontend_build:/build alpine ls /build/index.html 2>/dev/null; then
    echo "❌ Fix: Frontend build files missing - rebuild frontend"
    echo "   docker-compose -f docker-compose.prod.yml up --build frontend"
    echo "   docker-compose -f docker-compose.prod.yml logs frontend"
else
    echo "✅ Frontend build files exist - check nginx configuration"
    echo "   docker-compose -f docker-compose.prod.yml exec nginx nginx -t"
fi
