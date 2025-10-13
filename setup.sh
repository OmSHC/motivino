#!/bin/bash

# Setup script for Interactive Student Motivation News Website

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

echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Google OAuth2 and OpenAI API credentials"
echo "2. Start the development server: python manage.py runserver"
echo "3. Start Celery worker: celery -A motivation_news worker --loglevel=info"
echo "4. Start Celery beat: celery -A motivation_news beat --loglevel=info"
echo ""
echo "Access the admin interface at: http://localhost:8000/admin/"
echo "API documentation available at: http://localhost:8000/api/"
