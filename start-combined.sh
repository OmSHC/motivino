#!/bin/bash

# Startup script for combined container (Frontend + Backend + Nginx)

set -e

echo "🚀 Starting combined application server..."

# Function to handle shutdown gracefully
cleanup() {
    echo "🛑 Shutting down services..."
    kill $GUNICORN_PID $NGINX_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Create necessary directories
mkdir -p /app/logs /app/staticfiles /app/media /var/log/gunicorn

# Set proper ownership
chown -R django:django /app /var/log/gunicorn

# Switch to django user for running the application
su - django -c "
    # Run database migrations
    echo '🗄️ Running database migrations...'
    python manage.py migrate --noinput

    # Collect static files
    echo '📁 Collecting static files...'
    python manage.py collectstatic --noinput --clear
"

# Start Gunicorn (Django backend) in background
echo "🐍 Starting Gunicorn (Django backend)..."
su - django -c "gunicorn --bind 127.0.0.1:8000 --chdir /app motivation_news.wsgi:application --log-file /app/logs/gunicorn.log --access-logfile /app/logs/gunicorn-access.log --workers 3 --timeout 120" &
GUNICORN_PID=$!

# Wait a moment for Gunicorn to start
sleep 5

# Test if Gunicorn is running
if ! curl -f http://127.0.0.1:8000/api/core/health/ >/dev/null 2>&1; then
    echo "❌ Gunicorn failed to start properly"
    exit 1
fi

echo "✅ Gunicorn started successfully"

# Start Nginx in foreground (this will be the main process)
echo "🌐 Starting Nginx (reverse proxy)..."
nginx -g 'daemon off;' &
NGINX_PID=$!

# Wait for Nginx to start
sleep 2

# Test if Nginx is serving
if ! curl -f http://localhost/health >/dev/null 2>&1; then
    echo "❌ Nginx failed to start properly"
    exit 1
fi

echo "✅ Nginx started successfully"
echo "🎉 All services started! Application available on port 80"

# Wait for any process to exit
wait
