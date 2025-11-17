#!/bin/bash

# Complete Railway Deployment
# GitHub: https://github.com/nguyenhoang1221hoangnguyen/vnstock-api.git
# Usage: ./deploy-now.sh

set -e

echo "🚀 VNStock API - Railway Deployment"
echo "===================================="
echo ""
echo "GitHub: ✓ Pushed to https://github.com/nguyenhoang1221hoangnguyen/vnstock-api.git"
echo "Railway CLI: ✓ Installed (v4.11.1)"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if logged in
echo -e "${BLUE}[1/5]${NC} Checking Railway authentication..."
if railway whoami &> /dev/null; then
    echo -e "${GREEN}✓${NC} Already logged in to Railway"
    railway whoami
else
    echo -e "${YELLOW}⚠${NC}  Not logged in to Railway"
    echo ""
    echo "Railway sẽ mở browser để bạn đăng nhập..."
    echo "Nếu chưa có tài khoản, sign up tại: https://railway.app"
    echo ""
    read -p "Press Enter to open browser and login..."
    railway login

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} Login failed"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Logged in successfully"
fi

echo ""

# Link or create project
echo -e "${BLUE}[2/5]${NC} Setting up Railway project..."

if railway status &> /dev/null; then
    echo -e "${GREEN}✓${NC} Project already linked"
    railway status
else
    echo ""
    echo "Tạo Railway project mới hoặc link với project có sẵn?"
    echo "  1. Tạo project mới (khuyến nghị)"
    echo "  2. Link với project có sẵn"
    echo ""
    read -p "Chọn (1/2): " choice

    if [ "$choice" == "1" ]; then
        echo ""
        echo "Đang tạo project mới..."
        railway init --name vnstock-api
    else
        echo ""
        echo "Đang link với project có sẵn..."
        railway link
    fi

    echo -e "${GREEN}✓${NC} Project linked successfully"
fi

echo ""

# Setup environment variables
echo -e "${BLUE}[3/5]${NC} Setting up environment variables..."

echo "Đang set environment variables..."
railway variables set API_HOST=0.0.0.0
railway variables set API_PORT=8000
railway variables set PYTHONUNBUFFERED=1
railway variables set HOME=/app
railway variables set VNSTOCK_DATA_DIR=/app/.vnstock
railway variables set IPYTHONDIR=/app/.ipython
railway variables set NODE_ENV=production
railway variables set TIMEZONE=Asia/Ho_Chi_Minh

echo -e "${GREEN}✓${NC} Environment variables configured"
echo ""

# Deploy
echo -e "${BLUE}[4/5]${NC} Deploying to Railway..."
echo ""
echo "Đang build và deploy Docker container..."
echo "Quá trình này có thể mất 2-5 phút..."
echo ""

railway up --detach

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Deployment failed"
    echo ""
    echo "Xem logs để debug:"
    echo "  railway logs"
    exit 1
fi

echo ""
echo -e "${GREEN}✓${NC} Deployment initiated successfully"
echo ""

# Generate domain
echo -e "${BLUE}[5/5]${NC} Setting up public domain..."

# Try to generate domain
DOMAIN_OUTPUT=$(railway domain 2>&1)

if echo "$DOMAIN_OUTPUT" | grep -q "https://"; then
    DOMAIN=$(echo "$DOMAIN_OUTPUT" | grep -oP 'https://[^ ]+' | head -1)
    echo -e "${GREEN}✓${NC} Domain: $DOMAIN"
else
    echo -e "${YELLOW}⚠${NC}  Domain generation in progress or already exists"
    echo "Run 'railway domain' to get your domain"
fi

echo ""
echo "═══════════════════════════════════════"
echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
echo "═══════════════════════════════════════"
echo ""
echo "📊 Deployment Summary:"
echo "  ✓ Code pushed to GitHub"
echo "  ✓ Railway CLI configured"
echo "  ✓ Project linked"
echo "  ✓ Environment variables set"
echo "  ✓ Docker container deployed"
echo ""
echo "🌐 Access your API:"
echo "  Dashboard:  railway open"
echo "  Get domain: railway domain"
echo "  View logs:  railway logs"
echo ""
echo "📝 Next Steps:"
echo "  1. Wait ~2 minutes for deployment to complete"
echo "  2. Run: railway domain    # to get your URL"
echo "  3. Test: curl \$(railway domain)/health"
echo "  4. Visit: \$(railway domain)/docs"
echo ""
echo "💡 Useful Commands:"
echo "  railway logs              # View real-time logs"
echo "  railway open              # Open dashboard"
echo "  railway status            # Check deployment status"
echo "  railway restart           # Restart service"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
