#!/bin/bash

echo "🔥 Configuring GCP Firewall Rules..."

# Get VM external IP
VM_IP=$(curl -s ifconfig.me)
echo "VM External IP: $VM_IP"

# Create firewall rules to allow HTTP/HTTPS traffic
echo "Creating firewall rules..."

# Allow HTTP (port 80)
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic"

# Allow HTTPS (port 443) 
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS traffic"

# Allow Django backend (port 8000)
gcloud compute firewall-rules create allow-django \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Django backend access"

# Allow React frontend (port 3000) - if needed for direct access
gcloud compute firewall-rules create allow-react \
    --allow tcp:3000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow React frontend access"

echo "✅ Firewall rules created!"

echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://$VM_IP"
echo "   Backend API: http://$VM_IP/api"
echo "   Admin: http://$VM_IP/admin"
echo ""
echo "�� Alternative access methods:"
echo "   Direct Django: http://$VM_IP:8000"
echo "   Direct React: http://$VM_IP:3000"
echo ""
echo "📝 Note: If using a custom domain, update DNS A record to point to $VM_IP"
