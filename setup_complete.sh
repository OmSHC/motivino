#!/bin/bash

# Complete setup script for Interactive Student Motivation News Website

echo "🚀 Setting up Interactive Student Motivation News Website..."

# Check if Python 3.10+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p static
mkdir -p media
mkdir -p docs

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp env.example .env
    echo "📝 Please edit .env file with your actual configuration values"
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "Please create a superuser account:"
python manage.py createsuperuser

# Generate initial content
echo "📰 Generating initial content..."
python manage.py generate_content

# Seed sample data
echo "🌱 Seeding sample data..."
python manage.py seed_data

# Setup React frontend
echo "⚛️ Setting up React frontend..."
cd frontend
npm install
cd ..

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next Steps:"
echo "1. Edit .env file with your Google OAuth2 and OpenAI API credentials"
echo "2. Start Redis server: redis-server"
echo "3. Start Django server: python manage.py runserver"
echo "4. Start Celery worker: celery -A motivation_news worker --loglevel=info"
echo "5. Start Celery beat: celery -A motivation_news beat --loglevel=info"
echo "6. Start React frontend: cd frontend && npm start"
echo ""
echo "🌐 Access Points:"
echo "- Django Admin: http://localhost:8000/admin/"
echo "- API Documentation: http://localhost:8000/api/"
echo "- React Frontend: http://localhost:3000/"
echo ""
echo "📚 Documentation:"
echo "- Google OAuth Setup: docs/GOOGLE_OAUTH_SETUP.md"
echo "- API Reference: http://localhost:8000/api/"
echo ""
echo "🔧 Configuration Required:"
echo "- Google OAuth2 credentials in .env"
echo "- OpenAI API key in .env"
echo "- Redis server running for Celery"
