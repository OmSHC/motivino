#!/bin/bash

echo "🧪 Auth Testing Tool - With Proper Data"
echo "========================================"

# Test with minimal required data
echo ""
echo "📝 Testing Signup with Minimal Data:"
echo "POST http://136.115.200.36/api/users/signup/"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "first_name": "Test",
    "last_name": "User"
  }' \
  -w "\n📊 Status: %{http_code}\n" \
  -v 2>&1 | grep -E "(HTTP|Status:|error|Response)"

# Test login
echo ""
echo "🔑 Testing Login:"
echo "POST http://136.115.200.36/api/users/login/"
curl -X POST http://136.115.200.36/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }' \
  -w "\n📊 Status: %{http_code}\n" \
  -v 2>&1 | grep -E "(HTTP|Status:|error|Response)"

# Check backend logs for detailed validation errors
echo ""
echo "📋 Backend Validation Logs:"
docker-compose -f docker-compose.prod.yml logs backend --tail=50 | grep -E "(SIGNUP|LOGIN|❌|✅|⚠️|🎉|Processing|Received)" | tail -10

# Test with browser-like data
echo ""
echo "🌐 Testing with Browser-like Data (SignupForm.tsx):"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "browser@example.com",
    "password": "password123",
    "first_name": "Browser",
    "last_name": "Test",
    "grade": null,
    "school": null
  }' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

echo ""
echo "🔍 Analysis:"
echo "- Check if email validation passes"
echo "- Check if password length is >= 6"
echo "- Check if user already exists"
echo "- Check backend logs for specific validation errors"

echo ""
echo "🎯 Common 400 Causes:"
echo "1. Email format invalid"
echo "2. Password too short (< 6 chars)"
echo "3. User already exists"
echo "4. Missing required fields (email/password)"
echo "5. Invalid grade format (should be int or null)"

echo ""
echo "🛠️ Debug Commands:"
echo "docker-compose -f docker-compose.prod.yml logs backend -f | grep -E '(SIGNUP|LOGIN)'"
echo "docker-compose -f docker-compose.prod.yml exec backend python manage.py shell -c \"from apps.users.models import User; User.objects.filter(email='test@example.com').exists()\""
