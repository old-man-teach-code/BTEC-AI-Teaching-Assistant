#!/bin/bash

COMPOSE_FILES="-f docker-compose.yml"

echo "Chuẩn bị môi trường production..."
cp .env.prod .env

docker compose $COMPOSE_FILES up -d --build frontend-prod

echo "Đang khởi động frontend production, theo dõi log:"
docker compose $COMPOSE_FILES logs -f frontend-prod