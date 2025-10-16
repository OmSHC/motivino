#!/bin/bash

echo "🔍 Debug Nginx Configuration"
echo "==========================="

# Check if nginx config is valid
echo "1. Testing nginx configuration syntax:"
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Check what config file nginx is using
echo ""
echo "2. Nginx configuration files:"
docker-compose -f docker-compose.prod.yml exec nginx ls -la /etc/nginx/

# Check the actual nginx config being used
echo ""
echo "3. Current nginx configuration (/etc/nginx/nginx.conf):"
docker-compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/nginx.conf | head -20

# Check if our custom config is mounted
echo ""
echo "4. Checking mounted config:"
docker-compose -f docker-compose.prod.yml exec nginx ls -la /etc/nginx/nginx.conf
docker-compose -f docker-compose.prod.yml exec nginx wc -l /etc/nginx/nginx.conf

# Test nginx internal request handling
echo ""
echo "5. Testing nginx internal proxy:"
docker-compose -f docker-compose.prod.yml exec nginx curl -v http://backend:8000/api/core/health/ 2>&1 | head -10

# Test external request with verbose logging
echo ""
echo "6. Testing external request with curl verbose:"
curl -v -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"debug@example.com","password":"test123"}' \
  2>&1 | grep -E "(Trying|Connected|HTTP|<|Status:|400)" | head -10

# Check nginx access logs
echo ""
echo "7. Recent nginx access logs:"
docker-compose -f docker-compose.prod.yml exec nginx tail -20 /var/log/nginx/access.log 2>/dev/null || echo "No access log found"

# Check nginx error logs
echo ""
echo "8. Recent nginx error logs:"
docker-compose -f docker-compose.prod.yml exec nginx tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No error log found"

echo ""
echo "🎯 Possible Issues:"
echo "- Nginx not using our config file"
echo "- Config syntax error"
echo "- Request body size limits"
echo "- Missing proxy headers"
echo "- CORS preflight issues"

echo ""
echo "🛠️ Quick Fixes:"
echo "docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload"
echo "docker-compose -f docker-compose.prod.yml restart nginx"
