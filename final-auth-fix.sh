#!/bin/bash

echo "🎯 Final Auth Fix - Complete Service Rebuild"
echo "==========================================="

# Stop all services
echo "1. Stopping all services..."
docker-compose -f docker-compose.prod.yml down

# Remove nginx container to force clean rebuild
echo "2. Removing nginx container..."
docker rm -f motivino-nginx-1 2>/dev/null || true

# Start services in correct order: db/redis -> backend -> frontend -> nginx
echo "3. Starting database and Redis..."
docker-compose -f docker-compose.prod.yml up -d db redis

# Wait for db/redis to be healthy
echo "⏳ Waiting for database and Redis..."
sleep 15

# Check db/redis health
echo "Checking db/redis health..."
docker-compose -f docker-compose.prod.yml ps db redis

# Start backend
echo "4. Starting backend..."
docker-compose -f docker-compose.prod.yml up -d backend

# Wait for backend to be healthy
echo "⏳ Waiting for backend health check..."
sleep 45

# Check backend health
echo "Checking backend health..."
docker-compose -f docker-compose.prod.yml ps backend
curl -s http://localhost:8000/api/core/health/ || echo "❌ Backend not healthy yet"

# Build and run frontend
echo "5. Building frontend..."
docker-compose -f docker-compose.prod.yml up frontend

# Start nginx (will wait for backend to be healthy due to depends_on condition)
echo "6. Starting nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to start
echo "⏳ Waiting for nginx..."
sleep 10

# Test complete flow
echo ""
echo "🎯 Testing Complete Auth Flow:"
echo ""

# Test health endpoint
echo "Health endpoint:"
curl -s http://136.115.200.36/health/

# Test API through nginx
echo ""
echo "API signup test:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"final@example.com","password":"test123","first_name":"Final","last_name":"Test"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test login
echo ""
echo "API login test:"
curl -X POST http://136.115.200.36/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"final@example.com","password":"test123"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Check logs
echo ""
echo "📋 Auth logs:"
docker-compose -f docker-compose.prod.yml logs backend --tail=10 | grep -E "(SIGNUP|LOGIN|❌|✅)" | tail -5

echo ""
echo "🎉 Final Status:"
echo "- If signup returns 201: ✅ AUTH WORKING!"
echo "- If login returns 200: ✅ AUTH WORKING!"
echo "- Test from browser: http://136.115.200.36"
