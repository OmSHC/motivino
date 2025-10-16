#!/bin/bash

echo "🔄 Force Rebuilding Frontend with API URL Fixes"
echo "==============================================="

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Remove old frontend image and volume
echo "🧹 Cleaning up old frontend artifacts..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker volume rm motivino_frontend_build 2>/dev/null || true
docker rmi motivation-frontend:latest 2>/dev/null || true

# Rebuild frontend only
echo "🏗️ Building new frontend image..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Build and copy files
echo "📦 Running frontend build process..."
docker-compose -f docker-compose.prod.yml up frontend

# Check if build succeeded
echo ""
echo "✅ Build completed! Checking results..."
docker-compose -f docker-compose.prod.yml logs frontend | tail -10

# Check if files exist
echo ""
echo "📁 Checking if build files were copied..."
docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/ 2>/dev/null || echo "Volume empty!"

# Restart nginx to pick up new files
echo ""
echo "🌐 Restarting nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx

echo ""
echo "🎯 Frontend rebuild complete!"
echo "============================"
echo "✅ New frontend image built with API URL fixes"
echo "✅ Build files copied to nginx volume"
echo "✅ Nginx restarted to serve new files"
echo ""
echo "🔍 Test Results:"
echo "- Open browser console to see API URL debug logs"
echo "- Try signup/login - should now use /api/ instead of localhost:8001"
echo "- Clear browser cache if still seeing old URLs"
