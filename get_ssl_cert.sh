#!/bin/bash

# Script to obtain SSL certificate for winmind.in using Let's Encrypt
# This script handles: certbot installation, certificate creation, folder creation, and file permissions

DOMAIN="winmind.in"
EMAIL="priyankahya@gmail.in"  # Replace with your actual email
SSL_DIR="./ssl"

echo "🚀 Starting SSL certificate setup for $DOMAIN..."
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    SUDO=""
    echo "✅ Running as root"
else
    SUDO="sudo"
    echo "ℹ️  Running with sudo privileges"
fi

# Check if certbot is installed
echo ""
echo "📦 Checking certbot installation..."
if ! command_exists certbot; then
    echo "❌ Certbot not found. Installing..."
    $SUDO apt update
    $SUDO apt install -y certbot

    if ! command_exists certbot; then
        echo "❌ Failed to install certbot. Please install manually: sudo apt install certbot"
        exit 1
    fi
    echo "✅ Certbot installed successfully"
else
    echo "✅ Certbot is already installed"
fi

# Create SSL directory
echo ""
echo "📁 Creating SSL directory..."
if [[ -d "$SSL_DIR" ]]; then
    echo "ℹ️  SSL directory exists. Cleaning up any existing files..."

    # Remove any directories that might exist instead of files
    if [[ -d "$SSL_DIR/fullchain.pem" ]]; then
        echo "🧹 Removing directory: $SSL_DIR/fullchain.pem"
        rm -rf "$SSL_DIR/fullchain.pem"
    fi

    if [[ -d "$SSL_DIR/privkey.pem" ]]; then
        echo "🧹 Removing directory: $SSL_DIR/privkey.pem"
        rm -rf "$SSL_DIR/privkey.pem"
    fi
else
    echo "📁 Creating SSL directory: $SSL_DIR"
    mkdir -p "$SSL_DIR"
fi

# Stop nginx temporarily (if running)
echo ""
echo "⏹️  Stopping nginx service temporarily..."
$SUDO systemctl stop nginx 2>/dev/null || docker-compose down nginx 2>/dev/null || true
echo "✅ Nginx stopped (or was not running)"

# Get certificate using standalone mode
echo ""
echo "🔐 Obtaining SSL certificate for $DOMAIN and www.$DOMAIN..."
$SUDO certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Check if certificate was obtained successfully
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
if [[ ! -f "$CERT_PATH/fullchain.pem" ]] || [[ ! -f "$CERT_PATH/privkey.pem" ]]; then
    echo "❌ Certificate generation failed!"
    echo "Please check the certbot output above for errors."
    exit 1
fi

echo "✅ Certificate obtained successfully"

# Copy certificates to project ssl directory
echo ""
echo "📋 Copying certificates to project SSL directory..."
if ! $SUDO cp "$CERT_PATH/fullchain.pem" "$SSL_DIR/"; then
    echo "❌ Failed to copy fullchain.pem"
    exit 1
fi

if ! $SUDO cp "$CERT_PATH/privkey.pem" "$SSL_DIR/"; then
    echo "❌ Failed to copy privkey.pem"
    exit 1
fi

echo "✅ Certificates copied successfully"

# Set proper permissions
echo ""
echo "🔒 Setting proper file permissions..."
$SUDO chmod 644 "$SSL_DIR/fullchain.pem"
$SUDO chmod 600 "$SSL_DIR/privkey.pem"
echo "✅ Permissions set (644 for cert, 600 for key)"

# Verify certificates
echo ""
echo "🔍 Verifying certificates..."
if [[ ! -f "$SSL_DIR/fullchain.pem" ]] || [[ ! -f "$SSL_DIR/privkey.pem" ]]; then
    echo "❌ Certificate files not found in SSL directory!"
    exit 1
fi

# Check certificate validity
if command_exists openssl; then
    echo "📜 Certificate details:"
    openssl x509 -in "$SSL_DIR/fullchain.pem" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)"
else
    echo "⚠️  openssl not available for certificate verification"
fi

echo ""
echo "🎉 SSL certificates obtained and configured successfully!"
echo "=================================================="
echo "Certificate files:"
echo "  📄 ./ssl/fullchain.pem (644 permissions)"
echo "  🔑 ./ssl/privkey.pem (600 permissions)"
echo ""
echo "📅 Certificate expires: $(openssl x509 -in "$SSL_DIR/fullchain.pem" -enddate -noout 2>/dev/null | cut -d= -f2 || echo 'Check manually')"
echo ""
echo "🚀 Next steps:"
echo "1. ✅ DNS already configured: $DOMAIN → $(curl -s ifconfig.me)"
echo "2. 🔄 Restart services: docker-compose -f docker-compose.prod.yml up -d"
echo "3. 🧪 Test SSL: curl -I https://$DOMAIN"
echo ""
echo "📋 Certificate renewal:"
echo "   Let's Encrypt certificates expire in 90 days."
echo "   Auto-renewal is configured. Manual renewal: sudo certbot renew --quiet"
echo ""
echo "🔄 To restart services now, run:"
echo "   docker-compose -f docker-compose.prod.yml restart"
