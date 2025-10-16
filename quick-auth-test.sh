#!/bin/bash

echo "⚡ Quick Auth Test - Exact Frontend Data"
echo "======================================="

# Test backend directly (bypass nginx)
echo "Testing backend directly on port 8000..."
curl -X POST http://localhost:8000/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "grade": null,
    "school": null
  }' \
  -w "\n📊 Direct Backend Status: %{http_code}\n" \
  -s

echo ""
echo "Testing through nginx proxy..."
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "grade": null,
    "school": null
  }' \
  -w "\n📊 Nginx Proxy Status: %{http_code}\n" \
  -v 2>&1 | grep -E "(HTTP|<|Status:|400)" | head -10

echo ""
echo "📋 Backend Logs (last signup attempt):"
echo "Checking for SIGNUP logs..."
docker-compose -f docker-compose.prod.yml logs backend --tail=30 | grep -i signup || echo "❌ No signup logs found"

echo ""
echo "📋 All Recent Backend Logs:"
docker-compose -f docker-compose.prod.yml logs backend --tail=20

echo ""
echo "🐳 Backend Service Status:"
docker-compose -f docker-compose.prod.yml ps backend

echo ""
echo "🌐 Nginx Error Logs:"
docker-compose -f docker-compose.prod.yml logs nginx --tail=10 | grep -i error || echo "No nginx errors found"

echo ""
echo "🔍 Diagnosis:"
if curl -s http://localhost:8000/api/core/health/ > /dev/null 2>&1; then
    echo "✅ Backend is responding directly"
else
    echo "❌ Backend is NOT responding on port 8000"
fi

if curl -s http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ Nginx is responding"
else
    echo "❌ Nginx is NOT responding"
fi

echo ""
echo "🎯 If still 400, check these:"
echo "1. Email format validation"
echo "2. Password length (>=6)"
echo "3. User existence check"
echo "4. Null handling for grade/school"

echo ""
echo "🛠️ Manual Test:"
echo "curl -X POST http://136.115.200.36/api/users/signup/ -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"test123\",\"first_name\":\"Test\",\"last_name\":\"User\"}'"
