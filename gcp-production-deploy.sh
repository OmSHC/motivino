#!/bin/bash

set -e  # Exit on any error

echo "🚀 Production Deployment on GCP VM..."

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service health
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    log "⏳ Waiting for $service to be healthy..."
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml ps $service | grep -q "healthy\|running"; then
            log "✅ $service is ready!"
            return 0
        fi
        log "   Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 10
        ((attempt++))
    done

    log "❌ $service failed to start properly"
    return 1
}

# Check if Docker is installed
if ! command_exists docker; then
    log "🔧 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    log "✅ Docker installed. Please logout and login again, then run this script again"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    log "❌ .env file not found!"
    log "Please create .env file with your production settings first"
    echo "Required variables:"
    echo "  SECRET_KEY=your-secret-key"
    echo "  DATABASE_PASSWORD=your-database-password"
    echo "  DOMAIN=your-domain.com (optional)"
    exit 1
fi

# Load environment variables using a more portable method
set -a
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        case $key in
            ''|\#*) continue ;;
        esac
        # Remove quotes from value if present
        value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/")
        export "$key=$value"
    done < .env
    log "✅ Environment variables loaded from .env"
else
    log "⚠️  .env file not found, using environment defaults"
fi
set +a

log "🔧 Setting up production environment..."

# Create necessary directories with proper permissions
log "📁 Creating directories..."
sudo mkdir -p /opt/motivino/logs /opt/motivino/staticfiles /opt/motivino/media
sudo chown -R $USER:$USER /opt/motivino/logs /opt/motivino/staticfiles /opt/motivino/media

# Stop any existing containers and clean up
log "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Force stop any containers using our ports
log "🔌 Cleaning up port conflicts..."
docker ps -q | xargs -r docker stop || true
docker ps -aq | xargs -r docker rm || true

# Clean up unused Docker resources
log "🧹 Cleaning up Docker resources..."
docker system prune -f --volumes || true

# Handle Docker images
log "🐳 Setting up Docker images..."

# Check if we should skip image building entirely
if [ "$SKIP_BUILD" = "true" ]; then
    log "   ⏭️  Skipping image build (using existing images)..."
    log "   💡 Set SKIP_BUILD=false to rebuild images"
elif [ "$USE_REGISTRY" = "true" ] && [ -n "$REGISTRY_URL" ]; then
    log "   📥 Pulling pre-built images from registry: $REGISTRY_URL"
    log "   💡 This is the fastest option for production!"
    export BACKEND_IMAGE="$REGISTRY_URL/motivation-backend:latest"
    export FRONTEND_IMAGE="$REGISTRY_URL/motivation-frontend:latest"
    docker-compose -f docker-compose.prod.yml pull
else
    # Check if images already exist and are recent
    BACKEND_EXISTS=$(docker images -q motivation-backend:latest 2>/dev/null)
    FRONTEND_EXISTS=$(docker images -q motivation-frontend:latest 2>/dev/null)

    if [ "$FORCE_REBUILD" = "true" ] || [ -z "$BACKEND_EXISTS" ] || [ -z "$FRONTEND_EXISTS" ]; then
        if [ "$FORCE_REBUILD" = "true" ]; then
            log "   🔄 Force rebuilding all images (--no-cache)..."
            docker-compose -f docker-compose.prod.yml build --no-cache
        else
            log "   🏗️  Building missing images with layer caching..."
            # Build only missing images
            if [ -z "$BACKEND_EXISTS" ]; then
                log "     Building backend image..."
                docker-compose -f docker-compose.prod.yml build backend
            else
                log "     Backend image exists, skipping..."
            fi
            if [ -z "$FRONTEND_EXISTS" ]; then
                log "     Building frontend image..."
                docker-compose -f docker-compose.prod.yml build frontend
            else
                log "     Frontend image exists, skipping..."
            fi
        fi
        echo "$(date +%s)" > .last_build
    else
        log "   ✅ Using existing images (fastest option)..."
        log "   💡 Set FORCE_REBUILD=true to force rebuild"
        log "   💡 Set SKIP_BUILD=true to skip all image operations"
        log "   💡 Set USE_REGISTRY=true and REGISTRY_URL=gcr.io/project-id for production"
    fi
fi

# Start database and redis first
log "🚀 Starting database and Redis..."
docker-compose -f docker-compose.prod.yml up -d db redis

# Wait for database and Redis to be ready
wait_for_service db
wait_for_service redis

# Start backend service
log "🚀 Starting backend service..."
docker-compose -f docker-compose.prod.yml up -d backend

# Wait for backend to be ready (give it more time since it needs to run migrations)
log "⏳ Waiting for backend to start up (this may take a minute due to migrations)..."
sleep 45  # Give the backend time to start up before checking health

wait_for_service backend

# Run database migrations
log "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Collect static files
log "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput --clear

# Build frontend
log "🔨 Building frontend..."
if docker-compose -f docker-compose.prod.yml up frontend; then
    log "✅ Frontend build completed successfully"

    # Verify build output
    if docker run --rm -v $(pwd)/frontend_build:/build_output alpine ls -la /build_output/ | grep -q "index.html"; then
        log "✅ Frontend build files verified"
    else
        log "⚠️  Frontend build files not found in volume, but continuing..."
    fi
else
    log "❌ Frontend build failed! Checking build logs..."
    docker-compose -f docker-compose.prod.yml logs frontend
    exit 1
fi

# Start nginx
log "🚀 Starting nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to be ready
wait_for_service nginx

# Create admin user if specified
if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
    log "👤 Creating admin user..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py create_admin \
        --email="$ADMIN_EMAIL" \
        --password="$ADMIN_PASSWORD" \
        --first-name="${ADMIN_FIRST_NAME:-Admin}" \
        --last-name="${ADMIN_LAST_NAME:-User}" || true
else
    log "⚠️  Admin user not created. Set ADMIN_EMAIL and ADMIN_PASSWORD in .env to create one."
fi

# Get server IP
SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}' || echo "localhost")

log "✅ Production deployment complete!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://$SERVER_IP"
echo "   Backend API: http://$SERVER_IP/api"
echo "   Admin: http://$SERVER_IP/admin"
echo "   Health Check: http://$SERVER_IP/health"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   View specific service logs: docker-compose -f docker-compose.prod.yml logs -f <service>"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "   Quick update (no rebuild): docker-compose -f docker-compose.prod.yml up -d"
echo "   Skip all builds: SKIP_BUILD=true ./gcp-production-deploy.sh"
echo "   Force rebuild: FORCE_REBUILD=true ./gcp-production-deploy.sh"
echo "   Use registry: USE_REGISTRY=true REGISTRY_URL=gcr.io/project-id ./gcp-production-deploy.sh"
echo ""
# Health check
log "🔍 Running health checks..."
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🏥 Health Check Results:"
# Test nginx
if curl -f -s http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ Nginx: OK"
else
    echo "❌ Nginx: FAILED"
fi

# Test backend API
if curl -f -s http://localhost/api/ > /dev/null 2>&1; then
    echo "✅ Backend API: OK"
else
    echo "❌ Backend API: FAILED"
fi

# Test frontend
if curl -f -s -I http://localhost/ | grep -q "200\|301\|302"; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED"
fi

echo ""
echo "🎯 Deployment Summary:"
echo "   - All services should be running"
echo "   - Frontend served via nginx at http://$SERVER_IP"
echo "   - API available at http://$SERVER_IP/api"
echo "   - Admin panel at http://$SERVER_IP/admin"
echo "   - Health check at http://$SERVER_IP/health"
