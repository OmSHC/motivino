#!/bin/bash

echo "🔧 Fixing Database Tables Issue"
echo "=============================="

# Check if backend is running
if ! docker-compose -f docker-compose.prod.yml ps backend | grep -q "Up"; then
    echo "❌ Backend is not running. Starting it..."
    docker-compose -f docker-compose.prod.yml up -d backend

    # Wait for backend to be ready
    echo "⏳ Waiting for backend to start..."
    sleep 10
fi

echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"

    echo ""
    echo "🎯 Now you can create the admin user:"
    echo "===================================="
    echo "Method 1 - Using the setup script:"
    echo "  source admin-config.env && ./admin-setup.sh"
    echo ""
    echo "Method 2 - Manual creation:"
    echo "  docker-compose -f docker-compose.prod.yml exec backend python manage.py create_admin \\"
    echo "    --email your-email@example.com --password your-password \\"
    echo "    --first-name Admin --last-name User"
else
    echo "❌ Database migrations failed. Check the logs:"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi
