#!/bin/bash

echo "🧪 Test Nginx API Proxy Fix"
echo "==========================="

# Apply the nginx config fix
echo "1. Applying nginx configuration fix..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Config syntax OK, reloading nginx..."
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
else
    echo "❌ Config syntax error!"
    exit 1
fi

# Test backend direct access
echo ""
echo "2. Testing backend direct access:"
curl -X POST http://localhost:8000/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"direct@example.com","password":"test123","first_name":"Direct","last_name":"Test"}' \
  -w "\n📊 Direct Status: %{http_code}\n" \
  -s

# Test through nginx
echo ""
echo "3. Testing through nginx proxy:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"nginx@example.com","password":"test123","first_name":"Nginx","last_name":"Test"}' \
  -w "\n📊 Nginx Status: %{http_code}\n" \
  -s

# Check API access logs
echo ""
echo "4. Checking API access logs:"
docker-compose -f docker-compose.prod.yml exec nginx tail -10 /var/log/nginx/api_access.log 2>/dev/null || echo "No API access log found"

# Test with browser-like headers
echo ""
echo "5. Testing with browser-like request:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -H "Accept: application/json" \
  -d '{"email":"browser@example.com","password":"test123","first_name":"Browser","last_name":"Test"}' \
  -w "\n📊 Browser Status: %{http_code}\n" \
  -s

# Check auth logs
echo ""
echo "6. Checking auth logs for requests:"
docker-compose -f docker-compose.prod.yml logs backend --tail=10 | grep -E "(SIGNUP|LOGIN|❌|✅)" | tail -5

echo ""
echo "🎯 Results Analysis:"
echo "- If direct backend works but nginx fails: Proxy headers issue"
echo "- If both work: Fix successful!"
echo "- If both fail: Backend issue"
echo "- Check auth logs to see if requests reach Django"

echo ""
echo "📋 Next Steps:"
echo "1. If fixed: Test from browser"
echo "2. If still fails: Check proxy headers more carefully"
echo "3. Check nginx error logs: docker-compose logs nginx"
