#!/bin/bash

echo "🚀 Setting up Motivation News on GCP VM..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker and Docker Compose
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📦 Installing Git..."
sudo apt-get install -y git

# Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/OmSHC/motivino.git
cd motivino

# Set up environment
echo "⚙️ Setting up environment..."
cp .env.example .env

# Edit environment file
echo "📝 Please edit .env file with your settings:"
echo "   - SECRET_KEY: Generate a secure key"
echo "   - DATABASE_PASSWORD: Set a secure password"
echo "   - DOMAIN: Your domain name"
echo "   - OPENAI_API_KEY: Your OpenAI key (optional)"
echo ""
echo "Press Enter to continue after editing .env..."
read

# Start Docker services
echo "🚀 Starting Docker services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to start
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Create admin user
echo "👤 Creating admin user..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_admin

echo "✅ Setup complete!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api"
echo "   Admin: http://localhost/admin"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
