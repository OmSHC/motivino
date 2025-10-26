#!/bin/bash

echo "🔍 Debugging Content Rendering Issue on GCP"
echo "============================================="

echo ""
echo "1. Checking Docker containers status..."
docker-compose ps

echo ""
echo "2. Checking if @tailwindcss/typography is installed..."
docker-compose exec frontend npm list @tailwindcss/typography 2>/dev/null || echo "❌ Plugin not found"

echo ""
echo "3. Checking built CSS files..."
docker-compose exec frontend ls -la /app/build_output/static/css/ 2>/dev/null || echo "❌ CSS files not found"

echo ""
echo "4. Checking if prose classes are in CSS..."
docker-compose exec frontend grep -i "prose" /app/build_output/static/css/*.css 2>/dev/null | head -5 || echo "❌ Prose classes not found in CSS"

echo ""
echo "5. Checking nginx configuration..."
docker-compose exec nginx nginx -t 2>/dev/null || echo "❌ Nginx config error"

echo ""
echo "6. Checking frontend build logs..."
docker-compose logs frontend | tail -20

echo ""
echo "7. Checking if content is being served correctly..."
curl -s http://localhost | grep -i "prose" | head -3 || echo "❌ Prose classes not found in served HTML"

echo ""
echo "🔧 If issues found, try:"
echo "   docker-compose down"
echo "   docker-compose build --no-cache frontend"
echo "   docker-compose up -d"
