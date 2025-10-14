#!/bin/bash

echo "🔍 Troubleshooting GCP VM Issues..."

# Check disk space
echo "💾 Checking disk space..."
df -h

# Check Docker disk usage
echo "🐳 Checking Docker disk usage..."
docker system df

# Check running containers
echo "📦 Checking running containers..."
docker ps

# Check container logs for errors
echo "📋 Checking recent logs..."
docker-compose -f docker-compose.prod.yml logs --tail=20

# Clean up Docker
echo "🧹 Cleaning up Docker..."
docker system prune -f
docker volume prune -f

# Check if space is freed
echo "💾 Checking disk space after cleanup..."
df -h

echo "✅ Troubleshooting complete!"
echo ""
echo "🔧 Next steps:"
echo "1. If still low on space, resize your GCP VM disk"
echo "2. Try redeploying: sudo docker-compose -f docker-compose.prod.yml up --build -d"
echo "3. Check if frontend build errors are resolved"
