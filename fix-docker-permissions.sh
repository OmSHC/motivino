#!/bin/bash

echo "🔧 Fixing Docker permissions on GCP VM..."

# Method 1: Add user to docker group
echo "Adding user to docker group..."
sudo usermod -aG docker $USER

# Method 2: Start Docker daemon if not running
echo "Checking Docker daemon status..."
sudo systemctl status docker || sudo systemctl start docker

# Method 3: Alternative - use docker command with sudo
echo "Testing Docker with sudo..."
sudo docker --version

echo "✅ Docker setup complete!"
echo ""
echo "🔄 You need to logout and login again for group changes to take effect"
echo "   Or use 'sudo' with all docker commands"
echo ""
echo "Test with:"
echo "   sudo docker-compose -f docker-compose.prod.yml ps"
