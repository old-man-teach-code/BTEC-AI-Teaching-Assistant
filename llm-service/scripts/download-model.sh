#!/bin/bash

# Script download model cho AI Service
# Model: Arcee-VyLinh-Q4_K_M.gguf

set -e

MODEL_DIR="data/models"
MODEL_NAME="Arcee-VyLinh-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/Viet-Mistral/Arcee-VyLinh-Q4_K_M-gguf/resolve/main/Arcee-VyLinh-Q4_K_M.gguf"

echo "📥 AI Service Model Downloader"
echo "=============================="
echo "Model: $MODEL_NAME"
echo "Size: ~4.5GB"
echo ""

# Tạo thư mục nếu chưa có
mkdir -p $MODEL_DIR

# Kiểm tra model đã tồn tại chưa
if [ -f "$MODEL_DIR/$MODEL_NAME" ]; then
    echo "✅ Model đã tồn tại!"
    echo "   Path: $MODEL_DIR/$MODEL_NAME"
    
    # Kiểm tra kích thước
    SIZE=$(du -h "$MODEL_DIR/$MODEL_NAME" | cut -f1)
    echo "   Size: $SIZE"
    
    read -p "Bạn có muốn download lại không? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Kiểm tra công cụ download
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget -c -O"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -L -C - -o"
else
    echo "❌ Cần cài đặt wget hoặc curl để download!"
    exit 1
fi

# Download model
echo "🌐 Đang download model..."
echo "   URL: $MODEL_URL"
echo "   Destination: $MODEL_DIR/$MODEL_NAME"
echo ""
echo "⏳ Quá trình này có thể mất 10-30 phút tùy tốc độ mạng..."
echo ""

$DOWNLOAD_CMD "$MODEL_DIR/$MODEL_NAME" "$MODEL_URL"

# Kiểm tra download thành công
if [ -f "$MODEL_DIR/$MODEL_NAME" ]; then
    SIZE=$(du -h "$MODEL_DIR/$MODEL_NAME" | cut -f1)
    echo ""
    echo "✅ Download hoàn tất!"
    echo "   Model: $MODEL_DIR/$MODEL_NAME"
    echo "   Size: $SIZE"
    
    # Set permissions
    chmod 644 "$MODEL_DIR/$MODEL_NAME"
    
    echo ""
    echo "🎉 Model đã sẵn sàng để sử dụng!"
    echo "   Bạn có thể chạy: ./run-dev.sh"
else
    echo ""
    echo "❌ Download thất bại!"
    echo "   Vui lòng thử lại hoặc download thủ công từ:"
    echo "   $MODEL_URL"
    exit 1
fi