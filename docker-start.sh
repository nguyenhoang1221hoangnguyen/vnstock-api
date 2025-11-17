#!/bin/bash

# Script để khởi động VNStock API và n8n với Docker

echo "=========================================="
echo "VNStock API + n8n Docker Setup"
echo "=========================================="

# Kiểm tra Docker đã cài đặt chưa
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker chưa được cài đặt"
    echo "Vui lòng cài đặt Docker từ: https://www.docker.com/get-started"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose chưa được cài đặt"
    echo "Vui lòng cài đặt Docker Compose"
    exit 1
fi

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "📝 Tạo file .env từ .env.example..."
    cp .env.example .env
    echo "✅ File .env đã được tạo. Vui lòng kiểm tra và chỉnh sửa nếu cần."
fi

# Tạo thư mục cần thiết
echo "📁 Tạo thư mục cần thiết..."
mkdir -p logs
mkdir -p n8n/workflows

# Build và start containers
echo ""
echo "🏗️  Build Docker images..."
docker-compose build

echo ""
echo "🚀 Khởi động containers..."
docker-compose up -d

# Đợi services khởi động
echo ""
echo "⏳ Đang đợi services khởi động..."
sleep 5

# Kiểm tra trạng thái
echo ""
echo "📊 Kiểm tra trạng thái containers:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Setup hoàn tất!"
echo "=========================================="
echo ""
echo "📍 Services đang chạy tại:"
echo "   - VNStock API:  http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - n8n:          http://localhost:5678"
echo ""
echo "🔐 n8n Login:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo "   (Có thể thay đổi trong file .env)"
echo ""
echo "📝 Các lệnh hữu ích:"
echo "   - Xem logs:           docker-compose logs -f"
echo "   - Xem logs API:       docker-compose logs -f vnstock-api"
echo "   - Xem logs n8n:       docker-compose logs -f n8n"
echo "   - Dừng services:      docker-compose down"
echo "   - Khởi động lại:      docker-compose restart"
echo ""
echo "🔗 Kết nối từ n8n đến VNStock API:"
echo "   URL: http://vnstock-api:8000/api/stock/VNM"
echo "   (Sử dụng hostname 'vnstock-api' trong n8n)"
echo ""
echo "=========================================="
