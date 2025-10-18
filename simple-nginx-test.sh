#!/bin/bash

echo "🔧 Simple Nginx Fix Test"
echo "========================"

# First, check what config nginx is actually using
echo "1. What config is nginx using?"
docker-compose -f docker-compose.prod.yml exec nginx nginx -T | grep -A 5 "location /api/"

# If no /api/ location, our config isn't loaded
if ! docker-compose -f docker-compose.prod.yml exec nginx nginx -T | grep -q "location /api/"; then
    echo "❌ CRITICAL: /api/ location not found in nginx config!"
    echo "This means nginx is NOT using our custom config file!"

    # Check what config files exist
    echo ""
    echo "Available config files:"
    docker-compose -f docker-compose.prod.yml exec nginx find /etc/nginx -name "*.conf" -type f

    # Check if our config is there
    echo ""
    echo "Our config file:"
    ls -la nginx.conf

    # Force copy config and restart
    echo ""
    echo "🔄 Force copying config and restarting nginx..."
    docker-compose -f docker-compose.prod.yml exec nginx cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    docker-compose -f docker-compose.prod.yml restart nginx

    # Wait and check again
    sleep 3
    echo ""
    echo "After restart - checking config again:"
    docker-compose -f docker-compose.prod.yml exec nginx nginx -T | grep -A 5 "location /api/" || echo "Still no /api/ location!"
fi

# Test if /api/ location works now
echo ""
echo "2. Testing /api/ location:"
curl -X POST http://136.115.200.36/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"simple@example.com","password":"test123","first_name":"Simple","last_name":"Test"}' \
  -w "\n📊 Status: %{http_code}\n" \
  -s

# If still failing, check the most basic nginx config
if [ $? -ne 0 ] || [ "$(curl -s -o /dev/null -w "%{http_code}" http://136.115.200.36/api/users/signup/ -X POST -H "Content-Type: application/json" -d '{}')" = "400" ]; then
    echo ""
    echo "❌ Still failing. Creating minimal nginx config test..."

    # Create a minimal config to test
    cat > test-nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name _;

        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header Content-Type $http_content_type;
            proxy_set_header Content-Length $http_content_length;
        }

        location / {
            return 200 "nginx working\n";
        }
    }
}
EOF

    echo "Testing with minimal config..."
    docker run --rm -v $(pwd)/test-nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t
    if [ $? -eq 0 ]; then
        echo "✅ Minimal config works. The issue is in our complex config."
        echo "Let's simplify the /api/ block in nginx.conf"
    fi
fi

echo ""
echo "🎯 Summary:"
echo "If /api/ location not found: Nginx not using our config"
echo "If minimal config works: Our config has syntax issues"
echo "If still 400: Backend rejecting nginx requests"
