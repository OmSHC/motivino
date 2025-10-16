#!/bin/bash

echo "⚡ Quick Auth Test - Exact Frontend Data"
echo "======================================="

# Test exactly what SignupForm.tsx sends
echo "Testing with SignupForm.tsx data format..."
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
  -w "\n📊 Status: %{http_code}\n" \
  -v 2>&1 | grep -E "(HTTP|<|Status:)"

echo ""
echo "📋 Backend Logs (last signup attempt):"
docker-compose -f docker-compose.prod.yml logs backend --tail=20 | grep -A 10 -B 2 "SIGNUP REQUEST RECEIVED" | tail -15

echo ""
echo "🎯 If still 400, check these:"
echo "1. Email format validation"
echo "2. Password length (>=6)"
echo "3. User existence check"
echo "4. Null handling for grade/school"

echo ""
echo "🛠️ Manual Test:"
echo "curl -X POST http://136.115.200.36/api/users/signup/ -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"test123\",\"first_name\":\"Test\",\"last_name\":\"User\"}'"
