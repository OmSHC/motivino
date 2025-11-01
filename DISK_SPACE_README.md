# Disk Space Management for GCP Deployment

## 🚨 Problem: Frequent Disk Space Issues

Your GCP server has only **~10GB** total disk space, but Docker builds are failing due to "no space left on device" errors.

### Root Causes:
1. **Large build context**: Docker sends entire project directory (~591MB frontend/node_modules)
2. **No .dockerignore**: All files sent to Docker daemon
3. **Build cache accumulation**: Old build layers not cleaned
4. **Multiple image layers**: Inefficient Docker images

## ✅ Solutions Implemented

### 1. Created `.dockerignore` file
- Excludes `frontend/node_modules` (591MB saved)
- Excludes build artifacts, logs, IDE files
- Reduces build context from ~600MB to ~50MB

### 2. Added Cleanup Script (`cleanup-disk.sh`)
- Automated Docker cleanup (images, containers, volumes, cache)
- System package cleanup
- Log file rotation
- Run weekly to prevent space issues

### 3. Multi-stage Dockerfile (Optional)
- `Dockerfile.multi-stage` for even better efficiency
- Separate frontend build stage
- Only essential files in final image

## 🚀 Usage Instructions

### For Immediate Fix:
```bash
# On your GCP server
cd ~/motivino

# Run cleanup script
chmod +x cleanup-disk.sh
./cleanup-disk.sh

# Try build again
docker-compose -f docker-compose.prod.yml up --build -d
```

### For Ongoing Maintenance:
```bash
# Run weekly or when space gets low
./cleanup-disk.sh

# Check disk usage
df -h /

# Monitor Docker resources
docker system df
```

## 📊 Expected Results

**Before:**
- Build context: ~600MB
- Disk usage: 78% (2GB free)
- Frequent build failures

**After:**
- Build context: ~50MB (90% reduction!)
- Disk usage: ~50-60%
- Reliable builds
- Better performance

## 🔧 Alternative Solutions

### Option 1: Use Pre-built Images
```bash
# Build locally, push to registry
docker-compose build frontend backend
docker tag motivation-frontend:latest your-registry/motivation-frontend:latest
docker tag motivation-backend:latest your-registry/motivation-backend:latest
docker push your-registry/motivation-frontend:latest
docker push your-registry/motivation-backend:latest

# On GCP, just pull and run
docker-compose -f docker-compose.gcp.yml pull
docker-compose -f docker-compose.gcp.yml up -d
```

### Option 2: Increase GCP Disk Size
- Upgrade GCP VM disk from 10GB to 20-30GB
- More expensive but eliminates space issues entirely

### Option 3: Use Cloud Build
- Build images in Google Cloud Build
- Store in Google Container Registry
- Pull pre-built images on deployment

## 📈 Monitoring Commands

```bash
# Check disk usage
df -h /

# Docker resource usage
docker system df

# Largest directories
du -sh * | sort -hr | head -10

# Docker images
docker images

# Build context size (approximate)
du -sh . --exclude='frontend/node_modules'
```

## 🎯 Prevention Tips

1. **Run cleanup script weekly**
2. **Monitor disk usage regularly**
3. **Use .dockerignore for all projects**
4. **Clean build cache after deployments**
5. **Consider larger disk for production workloads**

The `.dockerignore` file alone should solve 90% of your disk space issues by preventing Docker from copying unnecessary files during builds.
