# Quick diagnostic of the current state
echo '=== NGINX HTML DIRECTORY ==='
docker-compose -f docker-compose.prod.yml exec nginx ls -la /usr/share/nginx/html/

echo ''
echo '=== FRONTEND BUILD VOLUME ==='
docker run --rm -v motivino_frontend_build:/build alpine ls -la /build/

echo ''
echo '=== DOCKER VOLUMES ==='
docker volume ls

echo ''
echo '=== CONTAINER STATUS ==='
docker-compose -f docker-compose.prod.yml ps

echo ''
echo '=== FRONTEND BUILD LOGS ==='
docker-compose -f docker-compose.prod.yml logs frontend | tail -10
