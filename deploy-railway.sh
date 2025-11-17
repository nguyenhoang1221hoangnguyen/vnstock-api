#!/bin/bash

# Railway Deployment Script for VNStock API
# Usage: ./deploy-railway.sh

set -e

echo "🚀 VNStock API - Railway Deployment Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI chưa được cài đặt${NC}"
    echo ""
    echo "Cài đặt Railway CLI:"
    echo "  macOS:   brew install railway"
    echo "  npm:     npm i -g @railway/cli"
    echo ""
    read -p "Bạn muốn cài đặt qua npm không? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm i -g @railway/cli
    else
        echo -e "${RED}Vui lòng cài đặt Railway CLI trước khi tiếp tục${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} Railway CLI đã được cài đặt"
echo ""

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Bạn chưa đăng nhập Railway${NC}"
    echo "Đang mở trình duyệt để đăng nhập..."
    railway login
    echo ""
fi

echo -e "${GREEN}✓${NC} Đã đăng nhập Railway"
echo ""

# Check if project is linked
if ! railway status &> /dev/null; then
    echo -e "${YELLOW}Project chưa được liên kết với Railway${NC}"
    echo ""
    echo "Chọn một trong hai:"
    echo "  1. Tạo project mới"
    echo "  2. Link với project có sẵn"
    echo ""
    read -p "Lựa chọn (1/2): " choice

    if [ "$choice" == "1" ]; then
        railway init
    else
        railway link
    fi
    echo ""
fi

echo -e "${GREEN}✓${NC} Project đã được liên kết"
echo ""

# Ask for environment setup
read -p "Bạn có muốn setup environment variables không? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Setting up environment variables..."

    # Set basic env vars
    railway variables set API_HOST=0.0.0.0
    railway variables set API_PORT=8000
    railway variables set PYTHONUNBUFFERED=1
    railway variables set HOME=/app
    railway variables set VNSTOCK_DATA_DIR=/app/.vnstock
    railway variables set IPYTHONDIR=/app/.ipython
    railway variables set NODE_ENV=production
    railway variables set TIMEZONE=Asia/Ho_Chi_Minh

    echo -e "${GREEN}✓${NC} Environment variables đã được set"
    echo ""
fi

# Deploy
echo "📦 Đang deploy lên Railway..."
echo ""
railway up

echo ""
echo -e "${GREEN}✓${NC} Deploy thành công!"
echo ""

# Generate domain if not exists
echo "🌐 Đang tạo public domain..."
railway domain 2>/dev/null || echo -e "${YELLOW}Domain đã tồn tại hoặc cần tạo thủ công${NC}"
echo ""

# Show deployment info
echo "📊 Deployment Information:"
echo "=========================="
railway status
echo ""

# Get the URL
echo -e "${GREEN}🎉 Deployment hoàn tất!${NC}"
echo ""
echo "Để xem logs: railway logs"
echo "Để mở dashboard: railway open"
echo "Để xem domain: railway domain"
echo ""
echo "API Documentation sẽ có tại:"
echo "  https://your-domain.up.railway.app/docs"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
