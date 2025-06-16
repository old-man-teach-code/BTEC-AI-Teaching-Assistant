#!/bin/bash

COMPOSE_FILES="-f docker-compose.yml"

# Đặt tên container riêng cho bot dev, ví dụ: discord_bot_dev
CONTAINER_NAME="discord_bot_dev"

if docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Container '$CONTAINER_NAME' đang chạy. Dừng docker compose..."
    docker compose $COMPOSE_FILES down
    exit 0
fi

# Ghi đè .env từ .env.dev (nếu có file này cho môi trường dev)
if [ -f ".env.dev" ]; then
    cp .env.dev .env
fi

echo "Khởi động môi trường development cho discord bot..."
docker compose $COMPOSE_FILES up -d --build

echo "Đang khởi động discord bot, theo dõi log realtime:"
docker compose $COMPOSE_FILES logs -f