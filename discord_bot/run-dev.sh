#!/bin/bash

COMPOSE_FILES="-f docker-compose.yml"
CONTAINER_NAME="discord_bot_dev"

# Hàm kiểm tra xem file .env đã có key cần thiết chưa
env_has_key() {
    local key="$1"
    [ -f .env ] && grep -q "^$key=" .env
}

# Nếu container đang chạy thì dừng lại
if docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Container '$CONTAINER_NAME' đang chạy. Dừng docker compose..."
    docker compose $COMPOSE_FILES down
    exit 0
fi

# Nếu chưa có .env hoặc .env chưa có DISCORD_TOKEN, thì mới copy từ .env.dev/.env.prod
if ! env_has_key "DISCORD_TOKEN"; then
    if [ -f ".env.dev" ]; then
        echo "Chưa tìm thấy DISCORD_TOKEN trong .env, copy từ .env.dev"
        cp .env.dev .env
    elif [ -f ".env.prod" ]; then
        echo "Chưa tìm thấy DISCORD_TOKEN trong .env, copy từ .env.prod"
        cp .env.prod .env
    else
        echo "Thiếu file .env/dev hoặc .env/prod! Vui lòng tạo thủ công file .env với DISCORD_TOKEN."
        exit 1
    fi
else
    echo "Đã tìm thấy DISCORD_TOKEN trong .env, giữ nguyên file .env."
fi

echo "Khởi động môi trường development cho discord bot..."
docker compose $COMPOSE_FILES up -d --build

echo "Đang khởi động discord bot, theo dõi log realtime:"
docker compose $COMPOSE_FILES logs -f