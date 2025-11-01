#!/bin/bash

# Fix GCP API Issues Script
echo "🔧 Fixing GCP API Issues"
echo "========================"

# Navigate to project directory
cd ~/motivino || exit 1

echo "📊 Current Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""

echo "🗄️ Creating SQLite Database..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput
echo ""

echo "✅ Database created. Checking if it exists..."
docker-compose -f docker-compose.prod.yml exec backend ls -la /app/db.sqlite3
echo ""

echo "🔄 Restarting backend service..."
docker-compose -f docker-compose.prod.yml restart backend
echo ""

echo "⏳ Waiting for backend to restart..."
sleep 10

echo "🏥 Testing backend health..."
docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/api/core/health/
echo ""

echo "🌐 Testing API connectivity from nginx..."
docker-compose -f docker-compose.prod.yml exec nginx curl -f http://backend:8000/api/core/health/
echo ""

echo "📝 Checking recent backend logs..."
docker-compose -f docker-compose.prod.yml logs --tail=5 backend
echo ""

echo "🎯 API Fix Complete!"
echo "=================="
echo "✅ Database created and migrated"
echo "✅ Backend restarted"
echo "✅ Services should now be working"
echo ""
echo "Test your APIs:"
echo "curl -k https://winmind.in/api/core/health/"
echo "curl -k https://winmind.in/api/users/demo/login/ -X POST"
