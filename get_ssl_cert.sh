#!/bin/bash

# Script to obtain SSL certificate for winmind.in using Let's Encrypt
# Requirements: certbot installed on your system

DOMAIN="winmind.in"
EMAIL="admin@winmind.in"  # Replace with your actual email

echo "Obtaining SSL certificate for $DOMAIN..."

# Stop nginx temporarily (if running)
echo "Stopping nginx service..."
sudo systemctl stop nginx 2>/dev/null || docker-compose down nginx 2>/dev/null || true

# Get certificate using standalone mode
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Copy certificates to project ssl directory
echo "Copying certificates to project ssl directory..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./ssl/

# Set proper permissions
sudo chmod 644 ./ssl/fullchain.pem
sudo chmod 600 ./ssl/privkey.pem

echo "SSL certificates obtained and copied successfully!"
echo "Certificate files:"
echo "  - ./ssl/fullchain.pem"
echo "  - ./ssl/privkey.pem"
echo ""
echo "Next steps:"
echo "1. Update your DNS to point $DOMAIN to your server IP"
echo "2. Run: docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "Note: Let's Encrypt certificates expire in 90 days."
echo "Set up auto-renewal with: sudo certbot renew --quiet"
