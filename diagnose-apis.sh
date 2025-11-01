#!/bin/bash

# API Failure Diagnosis Script for GCP
echo "🔍 API Failure Diagnosis"
echo "======================="

# Check current container status
echo "📊 Container Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""

# Check if services are healthy
echo "🏥 Health Checks:"
echo "Backend health:"
docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/api/core/health/ 2>/dev/null && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"
echo ""

echo "Redis health:"
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping 2>/dev/null && echo "✅ Redis healthy" || echo "❌ Redis unhealthy"
echo ""

# Check nginx configuration
echo "🌐 Nginx Configuration Check:"
docker-compose -f docker-compose.prod.yml exec nginx nginx -T 2>/dev/null | grep -A 5 -B 5 "location /api/" || echo "❌ Nginx config error"
echo ""

# Test internal networking
echo "🔗 Internal Network Tests:"
echo "Backend connectivity from nginx:"
docker-compose -f docker-compose.prod.yml exec nginx curl -f http://backend:8000/api/core/health/ 2>/dev/null && echo "✅ Backend reachable from nginx" || echo "❌ Backend not reachable from nginx"
echo ""

# Check backend logs
echo "📝 Recent Backend Logs:"
docker-compose -f docker-compose.prod.yml logs --tail=10 backend 2>/dev/null || echo "❌ Cannot access backend logs"
echo ""

# Check nginx logs
echo "📝 Recent Nginx Logs:"
docker-compose -f docker-compose.prod.yml logs --tail=10 nginx 2>/dev/null || echo "❌ Cannot access nginx logs"
echo ""

# Check if database exists
echo "🗄️ Database Check:"
docker-compose -f docker-compose.prod.yml exec backend ls -la /app/db.sqlite3 2>/dev/null && echo "✅ Database file exists" || echo "❌ Database file missing"
echo ""

# Check environment variables
echo "⚙️ Backend Environment (key variables):"
docker-compose -f docker-compose.prod.yml exec backend env | grep -E "(DATABASE_URL|REDIS_URL|DEBUG)" 2>/dev/null || echo "❌ Cannot access environment"
echo ""

echo "🎯 DIAGNOSIS SUMMARY:"
echo "======================"
echo "1. If backend is unhealthy: Check backend startup logs"
echo "2. If nginx config error: Check nginx.prod.conf syntax"
echo "3. If backend unreachable: Check Docker network connectivity"
echo "4. If database missing: Run migrations on backend"
echo "5. If environment empty: Check .env file and container restart"
echo ""
echo "💡 Quick fixes:"
echo "   # Restart all services"
echo "   docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "   # Rebuild and restart"
echo "   docker-compose -f docker-compose.prod.yml up --build -d"
echo ""
echo "   # Run migrations if DB issues"
echo "   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate"
