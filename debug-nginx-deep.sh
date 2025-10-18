#!/bin/bash

echo "🔍 Deep Nginx Debug - Config & Routing"
echo "====================================="

# Check if nginx actually reloaded
echo "1. Checking nginx process and config:"
docker-compose -f docker-compose.prod.yml exec nginx ps aux | grep nginx

# Check what config file is actually loaded
echo ""
echo "2. Current nginx master process config:"
docker-compose -f docker-compose.prod.yml exec nginx nginx -T | head -20

# Check all location blocks
echo ""
echo "3. All location blocks in config:"
docker-compose -f docker-compose.prod.yml exec nginx nginx -T | grep -A 5 -B 5 "location"

# Test if /api/ location matches
echo ""
echo "4. Testing /api/ location matching:"
curl -X GET http://136.115.200.36/api/ -v 2>&1 | grep -E "(HTTP|<|location:|Location:)" | head -5

# Test OPTIONS preflight
echo ""
echo "5. Testing OPTIONS preflight:"
curl -X OPTIONS http://136.115.200.36/api/users/signup/ \
  -H "Origin: http://136.115.200.36" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep -E "(HTTP|<|204)" | head -5

# Check if there's a default server block catching requests
echo ""
echo "6. Check for default server blocks:"
docker-compose -f docker-compose.prod.yml exec nginx nginx -T | grep -A 10 "server {"

# Test with explicit Host header
echo ""
echo "7. Testing with explicit Host header:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Host: 136.115.200.36" \
  -H "Content-Type: application/json" \
  -d '{"email":"host@example.com","password":"test123"}' \
  -v 2>&1 | grep -E "(HTTP|<)" | head -3

# Check if there's another nginx config
echo ""
echo "8. Check for additional config files:"
docker-compose -f docker-compose.prod.yml exec nginx find /etc/nginx -name "*.conf" -exec echo "=== {} ===" \; -exec cat {} \; | head -50

# Force nginx restart
echo ""
echo "9. Force nginx restart:"
docker-compose -f docker-compose.prod.yml restart nginx

# Test after restart
echo ""
echo "10. Test after nginx restart:"
sleep 3
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"restart@example.com","password":"test123","first_name":"Restart","last_name":"Test"}' \
  -w "\n📊 After Restart Status: %{http_code}\n" \
  -s

echo ""
echo "🎯 Analysis:"
echo "- If restart fixes it: Config reload issue"
echo "- If still 400: Location block not matching"
echo "- Check if multiple server blocks exist"
echo "- Verify /api/ location is in the correct server block"
