#!/bin/bash

echo "🧪 Testing Frontend Build Process"
echo "================================"

# Test the exact command used in docker-compose
echo "🔨 Testing build command..."

# Create a temporary container to test the build
docker run --rm \
  -v $(pwd)/frontend:/app \
  -w /app \
  --entrypoint sh \
  node:18-alpine \
  -c "
    echo 'Installing dependencies...'
    npm ci
    echo 'Building React app...'
    npm run build
    echo 'Checking build output...'
    ls -la build/
    echo 'Testing file copy...'
    mkdir -p /tmp/build_output
    cp -r build/* /tmp/build_output/ 2>/dev/null && echo 'Copy successful' || echo 'Copy failed'
    ls -la /tmp/build_output/
  "

echo ""
echo "✅ Build test completed"

# Now test with the actual volume
echo ""
echo "🔍 Testing with Docker Compose volume..."

# Clean up first
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker volume rm motivino_frontend_build 2>/dev/null || true

# Run frontend build
echo "Running frontend build..."
docker-compose -f docker-compose.prod.yml up frontend

# Check logs
echo ""
echo "📄 Build logs:"
docker-compose -f docker-compose.prod.yml logs frontend | tail -20

# Check volume contents
echo ""
echo "📁 Volume contents:"
docker run --rm -v motivino_frontend_build:/build alpine ls -la /build 2>/dev/null || echo "Volume is empty"

echo ""
echo "🎯 If volume is empty, the issue is in the docker-compose command"
echo "   The build/* files exist but aren't being copied to the volume"
