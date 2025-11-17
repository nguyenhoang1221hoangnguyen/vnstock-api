#!/bin/bash

# Script để dừng VNStock API và n8n Docker containers

echo "=========================================="
echo "Dừng VNStock API + n8n"
echo "=========================================="

# Dừng và xóa containers
echo "🛑 Dừng containers..."
docker-compose down

echo ""
echo "✅ Đã dừng tất cả services"
echo ""
echo "📝 Các lệnh hữu ích:"
echo "   - Khởi động lại:        ./docker-start.sh"
echo "   - Xóa volumes:          docker-compose down -v"
echo "   - Xóa images:           docker-compose down --rmi all"
echo "   - Xóa toàn bộ:          docker-compose down -v --rmi all"
echo ""
