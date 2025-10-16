# Check what's actually in the nginx html directory
docker-compose -f docker-compose.prod.yml exec nginx ls -la /usr/share/nginx/html/

# Check what's in the frontend build volume
docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/

# Check if volume exists
docker volume ls | grep frontend

# Check frontend container logs
docker-compose -f docker-compose.prod.yml logs frontend | tail -20
