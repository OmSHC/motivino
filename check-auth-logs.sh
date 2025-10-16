#!/bin/bash

echo "📋 Auth Error Log Checker"
echo "========================"

# Check if logs directory exists
echo "📁 Checking logs directory:"
docker-compose -f docker-compose.prod.yml exec backend ls -la /app/logs/ || echo "❌ Logs directory not found"

# Check auth debug log
echo ""
echo "🔍 Auth Debug Log (/app/logs/auth_debug.log):"
docker-compose -f docker-compose.prod.yml exec backend cat /app/logs/auth_debug.log 2>/dev/null | tail -10 || echo "❌ Debug log not found or empty"

# Check auth error log
echo ""
echo "❌ Auth Error Log (/app/logs/auth_errors.log):"
docker-compose -f docker-compose.prod.yml exec backend cat /app/logs/auth_errors.log 2>/dev/null | tail -10 || echo "❌ Error log not found or empty"

# Check Django logs
echo ""
echo "🐍 Django Logs (last auth entries):"
docker-compose -f docker-compose.prod.yml logs backend --tail=20 | grep -E "(SIGNUP|LOGIN|❌|✅)" | tail -10

# Check nginx error logs
echo ""
echo "🌐 Nginx Error Logs:"
docker-compose -f docker-compose.prod.yml logs nginx --tail=10 | grep -i error || echo "No nginx errors found"

echo ""
echo "🎯 Log File Locations:"
echo "- Auth Debug: /app/logs/auth_debug.log"
echo "- Auth Errors: /app/logs/auth_errors.log"
echo "- Django Logs: docker-compose logs backend"
echo "- Nginx Logs: docker-compose logs nginx"

echo ""
echo "🛠️ View Full Logs:"
echo "docker-compose -f docker-compose.prod.yml exec backend tail -f /app/logs/auth_errors.log"
echo "docker-compose -f docker-compose.prod.yml logs backend -f | grep -E '(SIGNUP|LOGIN)'"
