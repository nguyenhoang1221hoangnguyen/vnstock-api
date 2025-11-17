#!/bin/bash

# Script để rebuild Docker images

echo "=========================================="
echo "Rebuild VNStock API Docker Image"
echo "=========================================="

echo "🛑 Dừng containers..."
docker-compose down

echo ""
echo "🗑️  Xóa old images..."
docker-compose down --rmi local

echo ""
echo "🏗️  Rebuild images..."
docker-compose build --no-cache

echo ""
echo "🚀 Khởi động lại containers..."
docker-compose up -d

echo ""
echo "✅ Rebuild hoàn tất!"
echo ""
echo "📊 Trạng thái containers:"
docker-compose ps
