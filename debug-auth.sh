#!/bin/bash

echo "🔍 Auth API Debug Tool"
echo "======================"

# Test signup endpoint
echo ""
echo "📝 Testing Signup Endpoint..."
echo "POST http://localhost/api/users/signup/"
curl -X POST http://localhost/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "first_name": "Test",
    "last_name": "User",
    "grade": 10,
    "school": "Test School"
  }' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test login endpoint
echo ""
echo "🔑 Testing Login Endpoint..."
echo "POST http://localhost/api/users/login/"
curl -X POST http://localhost/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test admin login
echo ""
echo "👑 Testing Admin Login..."
echo "POST http://localhost/api/users/login/"
curl -X POST http://localhost/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "your-secure-password"
  }' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Check backend logs
echo ""
echo "📋 Backend Auth Logs (last 20 lines):"
docker-compose -f docker-compose.prod.yml logs backend --tail=20 | grep -E "(SIGNUP|LOGIN|❌|✅|⚠️|🎉)" || echo "No recent auth logs found"

echo ""
echo "🌐 External Access Test:"
echo "Testing from external IP..."
curl -X POST http://136.115.200.36/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' \
  -w "\n📊 External Status: %{http_code}\n" \
  -s --max-time 10

echo ""
echo "🎯 Quick Debug Commands:"
echo "docker-compose -f docker-compose.prod.yml logs backend -f | grep -E '(SIGNUP|LOGIN)'"
echo "docker-compose -f docker-compose.prod.yml exec backend python manage.py shell -c \"from apps.users.models import User; print('Users:', User.objects.all().count())\""
