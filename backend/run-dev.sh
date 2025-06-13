#!/bin/bash

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"

if docker ps --format '{{.Names}}' | grep -q "^fastapi_app$"; then
    echo "Container 'fastapi_app' đang chạy. Dừng docker-compose..."
    docker-compose $COMPOSE_FILES down
    exit 0
fi

echo "Container 'fastapi_app' chưa chạy. Khởi động môi trường development..."
cp .env.dev .env
docker-compose $COMPOSE_FILES up -d --build

# Đợi MySQL trên container db sẵn sàng
echo "Đợi MySQL sẵn sàng trên container db..."
until docker exec db mysqladmin ping -h"fastapi_mysql_db" --silent; do
    sleep 2
    echo "Chưa sẵn sàng, thử lại..."
done
echo "MySQL đã sẵn sàng!"

echo "Đợi container fastapi_app khởi động..."
while ! docker exec fastapi_app ls >/dev/null 2>&1; do
    sleep 1
done

echo "Tạo bảng database (nếu chưa có)..."
docker exec fastapi_app python -c "
import sys, os, glob, importlib
sys.path.insert(0, '/app')
try:
    from database.session import Base, engine
    models_dir = os.path.join('/app', 'models')
    for file in glob.glob(os.path.join(models_dir, '*.py')):
        name = os.path.splitext(os.path.basename(file))[0]
        if name != '__init__':
            importlib.import_module(f'models.{name}')
    Base.metadata.create_all(bind=engine)
    print('Đã tạo bảng thành công (hoặc đã tồn tại)')
except Exception as e:
    print('Lỗi khi tạo bảng:', e)
    sys.exit(1)
"

echo "Môi trường development đã sẵn sàng tại http://localhost:8000"
docker-compose $COMPOSE_FILES logs -f api