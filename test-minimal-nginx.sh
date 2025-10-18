#!/bin/bash

echo "🧪 Minimal Nginx Config Test"
echo "==========================="

# Create a minimal nginx config
cat > minimal-nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    resolver 127.0.0.11 valid=30s ipv6=off;

    server {
        listen 80;
        server_name _;

        # Health check
        location /health/ {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Simple API proxy
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header Content-Type $http_content_type;
        }

        # Catch all
        location / {
            return 200 "nginx minimal config working\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

echo "1. Testing minimal config syntax:"
docker run --rm -v $(pwd)/minimal-nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Minimal config syntax OK"

    echo ""
    echo "2. Testing minimal config with backend connectivity:"
    # Copy minimal config to container temporarily
    docker cp minimal-nginx.conf motivino-nginx-1:/etc/nginx/nginx.conf.test

    # Test if the minimal config would work
    docker-compose -f docker-compose.prod.yml exec nginx nginx -t -c /etc/nginx/nginx.conf.test

    if [ $? -eq 0 ]; then
        echo "✅ Minimal config would work"

        echo ""
        echo "3. Switching to minimal config temporarily:"
        docker-compose -f docker-compose.prod.yml exec nginx cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
        docker-compose -f docker-compose.prod.yml exec nginx cp /etc/nginx/nginx.conf.test /etc/nginx/nginx.conf
        docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

        echo ""
        echo "4. Testing with minimal config:"
        curl -X POST http://136.115.200.36/api/users/signup/ \
          -H "Content-Type: application/json" \
          -d '{"email":"minimal@example.com","password":"test123","first_name":"Minimal","last_name":"Test"}' \
          -w "\n📊 Minimal Config Status: %{http_code}\n" \
          -s

        echo ""
        echo "5. Restoring original config:"
        docker-compose -f docker-compose.prod.yml exec nginx cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
        docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

        echo ""
        echo "6. Testing restored config:"
        curl -X POST http://136.115.200.36/api/users/signup/ \
          -H "Content-Type: application/json" \
          -d '{"email":"restored@example.com","password":"test123","first_name":"Restored","last_name":"Test"}' \
          -w "\n📊 Restored Config Status: %{http_code}\n" \
          -s

    else
        echo "❌ Even minimal config fails - DNS issue?"
    fi
else
    echo "❌ Minimal config syntax error"
fi

# Cleanup
rm -f minimal-nginx.conf

echo ""
echo "🎯 Results:"
echo "- If minimal config works: Complex config has issues"
echo "- If minimal config fails: DNS/networking problem"
echo "- Check the difference between working and failing configs"
