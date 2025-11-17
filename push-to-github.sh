#!/bin/bash

# Push to GitHub Script
# Usage: ./push-to-github.sh

set -e

echo "🐙 Push VNStock API to GitHub"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Git chưa được khởi tạo. Đang khởi tạo..."
    git init
    git add .
    git commit -m "Initial commit - VNStock API v3.3.0"
fi

# Ask for GitHub URL
echo "Nhập GitHub repository URL của bạn:"
echo "Ví dụ: https://github.com/username/vnstock-api.git"
echo ""
read -p "URL: " github_url

# Validate URL
if [ -z "$github_url" ]; then
    echo "URL không được để trống!"
    exit 1
fi

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}Remote 'origin' đã tồn tại${NC}"
    read -p "Bạn có muốn thay thế bằng URL mới không? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        git remote add origin "$github_url"
        echo -e "${GREEN}✓${NC} Remote origin đã được cập nhật"
    fi
else
    git remote add origin "$github_url"
    echo -e "${GREEN}✓${NC} Remote origin đã được thêm"
fi

# Show current status
echo ""
echo "📊 Git Status:"
git remote -v
echo ""

# Confirm before push
read -p "Push code lên GitHub ngay bây giờ? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Hủy push. Bạn có thể push sau bằng lệnh: git push -u origin main"
    exit 0
fi

# Push to GitHub
echo ""
echo "📤 Đang push code lên GitHub..."
echo ""

# Try to push
if git push -u origin main; then
    echo ""
    echo -e "${GREEN}✓ Push thành công!${NC}"
    echo ""
    echo "🎉 Code đã được push lên GitHub!"
    echo ""
    echo "Repository của bạn: ${github_url%.git}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Push thất bại${NC}"
    echo ""
    echo "Có thể do:"
    echo "1. Cần authentication (Personal Access Token)"
    echo "2. Remote repository đã có code"
    echo ""
    echo "Giải pháp:"
    echo "  - Tạo Personal Access Token: https://github.com/settings/tokens"
    echo "  - Hoặc force push: git push -u origin main --force"
    echo ""
    read -p "Bạn có muốn force push không? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin main --force
        echo -e "${GREEN}✓ Force push thành công!${NC}"
    fi
fi

echo ""
echo "Next steps:"
echo "  1. Verify trên GitHub: ${github_url%.git}"
echo "  2. Deploy to Railway: ./deploy-railway.sh"
echo ""
