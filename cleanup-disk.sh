#!/bin/bash

# Disk Space Cleanup Script for GCP Server
echo "🧹 Starting disk cleanup..."

# Show current disk usage
echo "📊 Current disk usage:"
df -h /

# Clean Docker system
echo "🐳 Cleaning Docker..."
docker system prune -a --volumes -f

# Remove unused images
docker image prune -a -f

# Clean build cache
docker builder prune -a -f

# Remove stopped containers
docker container prune -f

# Clean system packages
echo "📦 Cleaning system packages..."
sudo apt autoremove -y
sudo apt autoclean -y

# Clean Docker buildx activity
rm -rf ~/.docker/buildx/activity/

# Remove old log files
echo "📝 Cleaning old logs..."
find ~/motivino/ -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

# Show disk usage after cleanup
echo "📊 Disk usage after cleanup:"
df -h /

echo "✅ Cleanup completed!"
