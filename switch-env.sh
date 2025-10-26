#!/bin/bash

# Script to switch between development and production nginx configurations

if [ "$1" = "dev" ]; then
    echo "🔧 Switching to DEVELOPMENT configuration..."
    echo "   - Using nginx.conf (HTTP only, no SSL)"
    echo "   - Perfect for local development"
    echo ""
    echo "✅ Development configuration is ready!"
    echo "   Run: docker-compose up -d"
    echo "   Access: http://localhost"
    
elif [ "$1" = "prod" ]; then
    echo "🚀 Switching to PRODUCTION configuration..."
    echo "   - Using nginx.prod.conf (HTTPS with SSL)"
    echo "   - Includes HTTP to HTTPS redirect"
    echo "   - Perfect for GCP deployment"
    echo ""
    echo "✅ Production configuration is ready!"
    echo "   Run: docker-compose -f docker-compose.prod.yml up -d"
    echo "   Access: https://your-domain.com"
    
else
    echo "Usage: $0 [dev|prod]"
    echo ""
    echo "  dev  - Use development configuration (HTTP only)"
    echo "  prod - Use production configuration (HTTPS with SSL)"
    echo ""
    echo "Current configurations:"
    echo "  📁 nginx.conf      - Development (HTTP only)"
    echo "  📁 nginx.prod.conf - Production (HTTPS + redirect)"
fi
