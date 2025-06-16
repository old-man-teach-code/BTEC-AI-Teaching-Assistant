#!/bin/bash

COMPOSE_FILES="-f docker-compose.yml"

if docker ps --format '{{.Names}}' | grep -q "^btecai_frontend_dev$"; then
    echo "Container 'btecai_frontend_dev' đang chạy. Dừng docker-compose..."
    docker compose $COMPOSE_FILES down
    exit 0
fi

# Ghi đè .env từ .env.dev khi chạy dev
cp .env.dev .env

docker compose $COMPOSE_FILES up -d --build frontend-dev

echo "Đang khởi động frontend, theo dõi log realtime:"
docker compose $COMPOSE_FILES logs -f frontend-dev