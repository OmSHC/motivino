#!/bin/bash

echo "🔍 Nginx 400 Error Investigation"
echo "==============================="

echo "Testing different request formats..."

# Test 1: Simple GET request
echo ""
echo "1. Testing GET request to health endpoint:"
curl -X GET http://136.115.200.36/health/ -w "\n📊 Status: %{http_code}\n" -s

# Test 2: Simple POST with minimal data
echo ""
echo "2. Testing POST with minimal JSON:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test 3: Check nginx configuration
echo ""
echo "3. Testing nginx config syntax:"
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t

# Test 4: Check if backend is responding
echo ""
echo "4. Testing direct backend access:"
curl -X POST http://localhost:8000/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -w "\n📊 Direct Status: %{http_code}\n" \
  -s

# Test 5: Check request size limits
echo ""
echo "5. Checking nginx limits in config:"
grep -E "(client_max_body_size|large_client_header_buffers)" nginx.conf || echo "No size limits found"

# Test 6: Check if it's a JSON parsing issue
echo ""
echo "6. Testing with form data instead of JSON:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=test123&first_name=Test&last_name=User" \
  -w "\n📊 Form Status: %{http_code}\n" \
  -s

echo ""
echo "🔍 Analysis:"
echo "- If GET works but POST fails: Likely nginx rejecting POST requests"
echo "- If direct backend works but nginx proxy fails: Nginx proxy issue"
echo "- If JSON fails but form data works: JSON parsing issue"
echo "- Check nginx error logs for 'client sent invalid request' or similar"
