#!/bin/bash

echo "🔧 Auth Fix Tool - Testing Backend Connectivity"
echo "==============================================="

# Check service status
echo ""
echo "🐳 Service Status:"
docker-compose -f docker-compose.prod.yml ps

# Test backend directly
echo ""
echo "🔗 Testing Backend Direct Access:"
echo "GET http://localhost:8000/api/core/health/"
curl -s http://localhost:8000/api/core/health/ || echo "❌ Backend not responding on port 8000"

# Test backend through nginx
echo ""
echo "🌐 Testing Through Nginx:"
echo "GET http://localhost/health/"
curl -s http://localhost/health/ || echo "❌ Nginx not responding"

# Test API through nginx
echo ""
echo "🔍 Testing API Through Nginx:"
echo "GET http://localhost/api/core/health/"
curl -s http://localhost/api/core/health/ || echo "❌ API proxy not working"

# Check nginx config
echo ""
echo "⚙️ Nginx Configuration Test:"
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t

# Check backend logs
echo ""
echo "📋 Backend Logs (last 10 lines):"
docker-compose -f docker-compose.prod.yml logs backend --tail=10

# Check nginx logs
echo ""
echo "📋 Nginx Logs (last 10 lines):"
docker-compose -f docker-compose.prod.yml logs nginx --tail=10

# Test URL routing
echo ""
echo "🎯 URL Routing Test:"
echo "Testing /api/users/login/ routing..."
curl -X POST http://localhost/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s | head -5

echo ""
echo "🔍 Diagnosis:"
echo "- If backend direct access fails: Backend service issue"
echo "- If nginx health fails: Nginx service issue"
echo "- If API through nginx fails but backend works: Nginx proxy issue"
echo "- If all fail: Both services down"

echo ""
echo "🛠️ Quick Fixes:"
echo "1. Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "2. Check backend: docker-compose -f docker-compose.prod.yml logs backend -f"
echo "3. Test backend: curl http://localhost:8000/api/core/health/"
