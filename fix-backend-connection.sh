#!/bin/bash

echo "🔧 Fix Backend Connection Issues"
echo "==============================="

# Check service status
echo "🐳 Current service status:"
docker-compose -f docker-compose.prod.yml ps

# Check if backend is accessible in Docker network
echo ""
echo "🔗 Testing backend in Docker network:"
docker-compose -f docker-compose.prod.yml exec nginx curl -s http://backend:8000/api/core/health/ || echo "❌ Backend not accessible from nginx container"

# Check Docker network
echo ""
echo "🌐 Docker network information:"
docker network ls | grep motivino

# Check containers in network
echo ""
echo "📋 Containers in motivino network:"
docker network inspect motivino_default | grep -A 5 -B 5 '"Name"\|"IPv4Address"'

# Restart services if needed
echo ""
echo "🔄 Restarting services to fix network issues..."
docker-compose -f docker-compose.prod.yml restart

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services..."
sleep 10

# Test again
echo ""
echo "🧪 Testing after restart:"
echo "Health endpoint:"
curl -s http://136.115.200.36/health/

echo ""
echo "API through nginx:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"test123","first_name":"New","last_name":"User"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

echo ""
echo "✅ If API works now, backend connection is fixed!"
echo "📋 Check logs: docker-compose -f docker-compose.prod.yml logs nginx"
