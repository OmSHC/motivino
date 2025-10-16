#!/bin/bash

echo "🔧 Fixing Frontend Build & Nginx Serving"
echo "======================================="

# Stop everything
echo "Stopping all services..."
docker-compose -f docker-compose.prod.yml down

# Clean up volumes
echo "Cleaning up volumes..."
docker volume rm motivino_frontend_build 2>/dev/null || echo "Volume didn't exist"

# Start just the frontend to build
echo "Building frontend..."
docker-compose -f docker-compose.prod.yml up frontend

# Check if build was successful
echo ""
echo "Checking build results..."
docker-compose -f docker-compose.prod.yml logs frontend | tail -5

# Check volume contents
echo ""
echo "Checking volume contents..."
docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/ 2>/dev/null || echo "Volume empty!"

# Start nginx
echo ""
echo "Starting nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait a moment
sleep 2

# Test nginx
echo ""
echo "Testing nginx..."
curl -s http://localhost/ | head -5

echo ""
echo "🎯 If you see HTML content above, the fix worked!"
echo "   If you still see nginx welcome page, check the volume contents."
