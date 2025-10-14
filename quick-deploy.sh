#!/bin/bash

echo "🚀 Quick Deploy - Skip Building, Just Restart Services"
echo "=================================================="

set -e

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if services are running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    log "🔄 Services are running, performing quick restart..."

    # Just restart without rebuilding
    docker-compose -f docker-compose.prod.yml restart

    log "✅ Services restarted successfully!"

    # Show status
    echo ""
    echo "📊 Service Status:"
    docker-compose -f docker-compose.prod.yml ps

    # Get server IP
    SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}' || echo "localhost")

    echo ""
    echo "🌐 Application URLs:"
    echo "   Frontend: http://$SERVER_IP"
    echo "   Backend API: http://$SERVER_IP/api"
    echo "   Admin: http://$SERVER_IP/admin"

else
    log "❌ No services running. Use full deployment:"
    echo "   ./gcp-production-deploy.sh"
    exit 1
fi
