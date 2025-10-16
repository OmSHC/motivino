#!/bin/bash

echo "👨‍💼 Setting up Persistent Admin User"
echo "==================================="

# Admin credentials (change these!)
ADMIN_EMAIL="admin@motivino.com"
ADMIN_PASSWORD="admin123!@#"
ADMIN_FIRST_NAME="System"
ADMIN_LAST_NAME="Administrator"

echo "📝 Admin User Details:"
echo "   Email: $ADMIN_EMAIL"
echo "   Password: $ADMIN_PASSWORD"
echo "   Name: $ADMIN_FIRST_NAME $ADMIN_LAST_NAME"
echo ""

# Check if backend is running
if ! docker-compose -f docker-compose.prod.yml ps backend | grep -q "Up"; then
    echo "❌ Backend is not running. Start it first:"
    echo "   docker-compose -f docker-compose.prod.yml up -d backend"
    exit 1
fi

echo "🔍 Checking if admin user already exists..."
if docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "
from apps.users.models import User
if User.objects.filter(email='$ADMIN_EMAIL').exists():
    print('EXISTS')
else:
    print('NOT_EXISTS')
" | grep -q "EXISTS"; then
    echo "✅ Admin user already exists in database"
    echo "   Email: $ADMIN_EMAIL"
    echo "   You can log in with the configured password"
else
    echo "👤 Creating admin user in database..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py create_admin \
        --email="$ADMIN_EMAIL" \
        --password="$ADMIN_PASSWORD" \
        --first-name="$ADMIN_FIRST_NAME" \
        --last-name="$ADMIN_LAST_NAME"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Admin user created successfully!"
        echo "   Email: $ADMIN_EMAIL"
        echo "   Password: $ADMIN_PASSWORD"
        echo ""
        echo "🔐 IMPORTANT: Change the default password after first login!"
        echo "   Go to your profile settings to update the password."
    else
        echo "❌ Failed to create admin user"
        exit 1
    fi
fi

echo ""
echo "🎯 Admin Login Information:"
echo "=========================="
echo "Frontend URL: http://$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')"
echo "Admin Email: $ADMIN_EMAIL"
echo "Admin Password: $ADMIN_PASSWORD"
echo ""
echo "Django Admin Panel: /admin/"
echo ""
echo "📋 Next Steps:"
echo "1. Visit the frontend URL above"
echo "2. Click 'Sign In' and use admin credentials"
echo "3. Access admin dashboard from the sidebar"
echo "4. Change the default password immediately!"
