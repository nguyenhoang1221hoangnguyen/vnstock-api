#!/bin/bash

# Complete Deployment Script
# Push to GitHub + Deploy to Railway
# Usage: ./deploy-all.sh

set -e

echo "🚀 VNStock API - Complete Deployment"
echo "====================================="
echo ""
echo "Workflow này sẽ:"
echo "  1. Push code lên GitHub"
echo "  2. Deploy lên Railway"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Push to GitHub
echo -e "${BLUE}[1/2] Pushing to GitHub...${NC}"
echo ""

./push-to-github.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ GitHub push failed${NC}"
    echo "Vui lòng kiểm tra lỗi và thử lại"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ GitHub push completed${NC}"
echo ""
echo "---"
echo ""

# Step 2: Deploy to Railway
echo -e "${BLUE}[2/2] Deploying to Railway...${NC}"
echo ""

# Ask if user wants to continue
read -p "Tiếp tục deploy lên Railway? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment đã dừng lại sau GitHub push"
    echo "Bạn có thể deploy sau bằng lệnh: ./deploy-railway.sh"
    exit 0
fi

echo ""
./deploy-railway.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Railway deployment failed${NC}"
    echo ""
    echo "Bạn có thể:"
    echo "  1. Deploy thủ công từ Railway Dashboard"
    echo "  2. Thử lại: ./deploy-railway.sh"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Railway deployment completed${NC}"
echo ""
echo "---"
echo ""

# Summary
echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
echo ""
echo "📊 Summary:"
echo "  ✓ Code pushed to GitHub"
echo "  ✓ API deployed to Railway"
echo ""
echo "🌐 Your API is now live!"
echo ""
echo "Next steps:"
echo "  - Check Railway dashboard: railway open"
echo "  - View logs: railway logs"
echo "  - Get URL: railway domain"
echo "  - Test API: curl https://your-domain.up.railway.app/health"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
