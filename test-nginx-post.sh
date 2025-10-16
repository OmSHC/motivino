#!/bin/bash

echo "🧪 Test Nginx POST Handling"
echo "=========================="

# Test 1: Simple POST to nginx health (should work)
echo "1. POST to health endpoint (should work):"
curl -X POST http://136.115.200.36/health/ \
  -H "Content-Type: text/plain" \
  -d "test" \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test 2: POST to API with minimal data
echo ""
echo "2. POST to API with minimal JSON:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test 3: Check if it's JSON specific
echo ""
echo "3. POST to API with form data:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=test123" \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test 4: Check request size limits
echo ""
echo "4. Check nginx config for body size limits:"
grep -E "(client_max_body_size|client_body_buffer_size)" nginx.conf || echo "No body size limits found in config"

# Test 5: Try OPTIONS preflight (CORS)
echo ""
echo "5. Test OPTIONS request (CORS preflight):"
curl -X OPTIONS http://136.115.200.36/api/users/signup/ \
  -H "Origin: http://136.115.200.36" \
  -H "Access-Control-Request-Method: POST" \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# Test 6: Check if nginx is rejecting based on User-Agent or other headers
echo ""
echo "6. Test with minimal headers:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -H "User-Agent: curl/7.68.0" \
  -d '{"email":"test@example.com"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

echo ""
echo "🔍 Analysis:"
echo "- If POST to /health/ works: Nginx handles POST fine"
echo "- If POST to /api/ fails: Issue with /api/ location block"
echo "- If JSON fails but form data works: JSON parsing issue"
echo "- If OPTIONS fails: CORS configuration issue"

echo ""
echo "🎯 Likely Issues:"
echo "1. Nginx client_max_body_size too small"
echo "2. Malformed JSON causing nginx to reject"
echo "3. Location block configuration issue"
echo "4. Missing proxy headers causing backend rejection"
