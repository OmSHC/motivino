#!/bin/bash

echo "🔥 Fixing GCP VM Access Issues..."

# Get VM external IP
VM_IP=$(curl -s ifconfig.me)
echo "VM External IP: $VM_IP"

# Check current firewall rules
echo "Current firewall rules:"
gcloud compute firewall-rules list --filter="name~allow"

# Create firewall rules for web access
echo "Creating firewall rules..."

# Allow HTTP (port 80)
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic for web application"

# Allow HTTPS (port 443)
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS traffic for web application"

# Allow Django backend (port 8000)
gcloud compute firewall-rules create allow-django \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Django backend access"

echo "✅ Firewall rules created!"

# Test connectivity
echo "Testing connectivity..."
echo "Testing port 80..."
curl -I http://$VM_IP/ 2>/dev/null | head -1

echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://$VM_IP"
echo "   Backend API: http://$VM_IP/api"
echo "   Admin: http://$VM_IP/admin"
echo ""
echo "🔧 Alternative access:"
echo "   Direct Django: http://$VM_IP:8000"
echo "   Direct React: http://$VM_IP:3000"
echo ""
echo "📝 If using a custom domain:"
echo "   Update DNS A record to point to: $VM_IP"
