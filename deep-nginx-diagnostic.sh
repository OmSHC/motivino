#!/bin/bash

echo "🔬 Deep Nginx API Diagnostic"
echo "==========================="

# Check what nginx is actually running
echo "1. Current nginx config in running container:"
docker-compose -f docker-compose.prod.yml exec nginx nginx -T | grep -A 10 -B 5 "location /api/"

# Test if /api/ location is being matched at all
echo ""
echo "2. Testing different API endpoints:"
echo "GET /api/:"
curl -X GET http://136.115.200.36/api/ -v 2>&1 | grep -E "(HTTP|<|location:|Location:|X-Accel)" | head -5

echo ""
echo "POST /api/test:"
curl -X POST http://136.115.200.36/api/test \
  -H "Content-Type: application/json" \
  -d '{}' \
  -v 2>&1 | grep -E "(HTTP|<|location:|Location:)" | head -5

# Test backend connectivity from nginx container
echo ""
echo "3. Backend connectivity from nginx container:"
docker-compose -f docker-compose.prod.yml exec nginx curl -v http://backend:8000/api/core/health/ 2>&1 | head -10

# Check if the resolver is working
echo ""
echo "4. DNS resolution test:"
docker-compose -f docker-compose.prod.yml exec nginx nslookup backend 2>/dev/null || echo "nslookup not available"

# Test direct backend access
echo ""
echo "5. Direct backend access:"
curl -X POST http://localhost:8000/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"direct-test@example.com","password":"test123","first_name":"Direct","last_name":"Test"}' \
  -w "\n📊 Direct Backend Status: %{http_code}\n" \
  -s

# Check nginx access logs for API requests
echo ""
echo "6. Nginx access logs:"
docker-compose -f docker-compose.prod.yml exec nginx tail -20 /var/log/nginx/access.log 2>/dev/null || echo "No access log found"

# Check if API access log exists
echo ""
echo "7. API specific access log:"
docker-compose -f docker-compose.prod.yml exec nginx ls -la /var/log/nginx/ 2>/dev/null
docker-compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/api_access.log 2>/dev/null || echo "API access log empty or doesn't exist"

# Test with a simple location block
echo ""
echo "8. Testing with curl verbose to see exact nginx response:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -H "User-Agent: TestScript/1.0" \
  -d '{"email":"verbose-test@example.com","password":"test123"}' \
  -v 2>&1 | grep -E "(Trying|Connected|HTTP|<|> |location:|Location:|Server:|Content-Type:)" | head -15

echo ""
echo "🔍 Analysis:"
echo "- If backend works directly: Backend is fine"
echo "- If nginx can curl backend: Network connectivity OK"
echo "- If API location not in config: Config issue"
echo "- If 400 with no backend logs: Nginx rejecting before proxy"
echo "- If 400 with backend logs: Backend rejecting request"

echo ""
echo "🎯 Next Steps:"
echo "1. Check if /api/ location block exists in nginx config"
echo "2. Verify proxy_pass URL is correct"
echo "3. Check if backend receives requests from nginx"
echo "4. Test with minimal location block"
