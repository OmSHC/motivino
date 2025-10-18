#!/bin/bash

echo "🔄 Quick Nginx Restart with Fixed Config"
echo "========================================"

# Force remove the broken nginx container
echo "1. Removing broken nginx container..."
docker-compose -f docker-compose.prod.yml stop nginx
docker rm -f motivino-nginx-1 2>/dev/null || true

# Wait a moment
sleep 2

# Start nginx fresh
echo "2. Starting nginx with fixed config..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for it to start
echo "⏳ Waiting for nginx to start..."
sleep 5

# Check if nginx is running
echo "3. Checking nginx status..."
docker-compose -f docker-compose.prod.yml ps nginx

# Test health endpoint
echo "4. Testing health endpoint:"
curl -s http://136.115.200.36/health/

# Test API
echo ""
echo "5. Testing API signup:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"restart@example.com","password":"test123","first_name":"Restart","last_name":"Test"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

echo ""
echo "✅ If API returns 201, nginx is working!"
echo "🌐 Test in browser: http://136.115.200.36"
