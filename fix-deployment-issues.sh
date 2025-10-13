#!/bin/bash

echo "🔧 Fixing Docker deployment issues..."

# Fix 1: Create logs directory with proper permissions
echo "📁 Creating logs directory..."
sudo mkdir -p /opt/motivino/logs
sudo chmod 755 /opt/motivino/logs
sudo chown $USER:$USER /opt/motivino/logs

# Fix 2: Create media directory with proper permissions
echo "�� Creating media directory..."
sudo mkdir -p /opt/motivino/media
sudo chmod 755 /opt/motivino/media
sudo chown $USER:$USER /opt/motivino/media

# Fix 3: Create staticfiles directory with proper permissions
echo "📁 Creating staticfiles directory..."
sudo mkdir -p /opt/motivino/staticfiles
sudo chmod 755 /opt/motivino/staticfiles
sudo chown $USER:$USER /opt/motivino/staticfiles

# Fix 4: Update docker-compose.prod.yml to fix nginx mounting issues
echo "🐳 Updating docker-compose configuration..."
sed -i 's|      - ./logs:/var/log/nginx|      - /opt/motivino/logs:/var/log/nginx|' docker-compose.prod.yml
sed -i 's|      - ./media:/usr/share/nginx/html/media:ro|      - /opt/motivino/media:/usr/share/nginx/html/media|' docker-compose.prod.yml
sed -i 's|      - ./staticfiles:/usr/share/nginx/html/static:ro|      - /opt/motivino/staticfiles:/usr/share/nginx/html/static|' docker-compose.prod.yml

echo "✅ Fixed deployment issues!"

# Restart services
echo "🔄 Restarting services..."
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up --build -d

echo "⏳ Waiting for services to start..."
sleep 30

# Test the deployment
echo "🧪 Testing deployment..."
sudo docker-compose -f docker-compose.prod.yml ps

echo "🌐 Testing application access..."
curl -s http://localhost/api/ | head -5

echo "✅ Deployment fixed and tested!"
