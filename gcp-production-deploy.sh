#!/bin/bash

echo "🚀 Production Deployment on GCP VM..."

# Fix Docker permissions first
echo "🔧 Setting up Docker permissions..."
if ! docker --version > /dev/null 2>&1; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Please logout and login again, then run this script again"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your production settings first"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

echo "🔧 Setting up production environment..."

# Create necessary directories
echo "📁 Creating directories..."
sudo mkdir -p /opt/motivino/logs /opt/motivino/staticfiles /opt/motivino/media

# Set proper permissions
sudo chown -R $USER:$USER /opt/motivino/logs /opt/motivino/staticfiles /opt/motivino/media

# Build and start services
echo "🐳 Building Docker images..."
sudo docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting services..."
sudo docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run migrations
echo "🗄️ Running database migrations..."
sudo docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
sudo docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Create admin user
echo "👤 Creating admin user..."
sudo docker-compose -f docker-compose.prod.yml exec backend python manage.py create_admin

echo "✅ Production deployment complete!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://$(curl -s ifconfig.me)"
echo "   Backend API: http://$(curl -s ifconfig.me)/api"
echo "   Admin: http://$(curl -s ifconfig.me)/admin"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: sudo docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: sudo docker-compose -f docker-compose.prod.yml down"
echo "   Restart: sudo docker-compose -f docker-compose.prod.yml restart"
echo "   Update: git pull && sudo docker-compose -f docker-compose.prod.yml up --build -d"
