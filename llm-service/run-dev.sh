#!/bin/bash

# Script khởi động môi trường development cho AI Service
# Tương tự như backend service

set -e  # Exit on error

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
SERVICE_NAME="ai-service"
BACKEND_NETWORK="backend_default"

echo "🤖 AI Teaching Assistant Service - Development Mode"
echo "=================================================="

# Kiểm tra Docker và Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker chưa được cài đặt. Vui lòng cài Docker trước."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose chưa được cài đặt. Vui lòng cài Docker Compose trước."
    exit 1
fi

# Kiểm tra service đang chạy hay không
if docker ps --format '{{.Names}}' | grep -q "^ai_service$"; then
    echo "🛑 Container 'ai_service' đang chạy. Đang dừng..."
    docker-compose $COMPOSE_FILES down
    exit 0
fi

echo "🚀 Khởi động môi trường development..."

# Copy environment file
cp .env.dev .env

# Tạo thư mục cần thiết
echo "📁 Tạo thư mục data..."
mkdir -p data/models data/chroma_db

# Kiểm tra model file
MODEL_FILE="data/models/Arcee-VyLinh-Q4_K_M.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "⚠️  CẢNH BÁO: Không tìm thấy model file!"
    echo "📥 Vui lòng download model từ:"
    echo "   https://huggingface.co/Viet-Mistral/Arcee-VyLinh-Q4_K_M-gguf"
    echo "   và đặt vào: $MODEL_FILE"
    echo ""
    read -p "Bạn có muốn tiếp tục không? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Kiểm tra backend network
echo "🔗 Kiểm tra kết nối với Backend service..."
if ! docker network ls | grep -q "$BACKEND_NETWORK"; then
    echo "⚠️  Network '$BACKEND_NETWORK' không tồn tại!"
    echo "   Vui lòng chạy Backend service trước."
    echo "   cd ../backend && ./run-dev.sh"
    exit 1
fi

# Kiểm tra backend database
if ! docker ps | grep -q "fastapi_mysql_db"; then
    echo "⚠️  Backend MySQL database không chạy!"
    echo "   Vui lòng chạy Backend service trước."
    exit 1
fi

# Build và start services
echo "🏗️  Building AI Service..."
docker-compose $COMPOSE_FILES build

echo "🚀 Starting AI Service..."
docker-compose $COMPOSE_FILES up -d

# Đợi service khởi động
echo "⏳ Đợi AI Service khởi động..."
sleep 5

# Kiểm tra health
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ AI Service đã sẵn sàng!"
        break
    fi
    
    echo -n "."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo "❌ AI Service không thể khởi động. Kiểm tra logs:"
    docker-compose $COMPOSE_FILES logs ai-service
    exit 1
fi

# Hiển thị thông tin
echo ""
echo "✨ AI Service Development Environment Ready!"
echo "============================================"
echo "📍 API URL:        http://localhost:8001"
echo "📚 API Docs:       http://localhost:8001/docs"
echo "📊 ReDoc:          http://localhost:8001/redoc"
echo "🔍 Health Check:   http://localhost:8001/health"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:    docker-compose $COMPOSE_FILES logs -f ai-service"
echo "   - Stop:         docker-compose $COMPOSE_FILES down"
echo "   - Restart:      docker-compose $COMPOSE_FILES restart ai-service"
echo "   - Shell:        docker-compose $COMPOSE_FILES exec ai-service bash"
echo ""
echo "🔥 Hot reload đã được bật - code changes sẽ tự động reload!"

# Theo dõi logs
echo ""
read -p "Bạn có muốn xem logs không? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    docker-compose $COMPOSE_FILES logs -f ai-service
fi