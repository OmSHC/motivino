#!/bin/bash

echo "🔍 Testing Docker Volume Sharing"
echo "==============================="

echo "1. Creating test file in volume..."
docker run --rm -v motivino_frontend_build:/test alpine sh -c "echo 'test content' > /test/test.txt && ls -la /test/"

echo ""
echo "2. Checking if file persists in volume..."
docker run --rm -v motivino_frontend_build:/test alpine ls -la /test/

echo ""
echo "3. Checking nginx access to volume..."
docker-compose -f docker-compose.prod.yml exec nginx ls -la /usr/share/nginx/html/

echo ""
echo "4. Testing volume content from nginx..."
docker-compose -f docker-compose.prod.yml exec nginx sh -c "echo 'nginx can write' > /usr/share/nginx/html/test-nginx.txt"
docker run --rm -v motivino_frontend_build:/test alpine ls -la /test/

echo ""
echo "5. Current volume info:"
docker volume inspect motivino_frontend_build

echo ""
echo "🎯 CONCLUSION:"
echo "If nginx can write to the volume, the mounting is working."
echo "If frontend copies files to the volume, nginx should see them."
