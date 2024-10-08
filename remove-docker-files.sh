#!/usr/bin/fish

echo "Stop all containers..."
docker ps -q | xargs -I {} docker stop {}
docker compose down

echo "Delete all containers..."
docker ps -a -q | xargs -I {} docker rm {}

echo "Delete all images..."
docker images -q | xargs -I {} docker rmi -f {}

echo "Delete allvolumes..."
docker volume ls -q | xargs -I {} docker volume rm {}
