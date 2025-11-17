#!/bin/bash

# Deploy n8n to Railway as separate service
# Usage: ./deploy-n8n-railway.sh

set -e

echo "🔧 Deploy n8n to Railway"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "Railway CLI chưa được cài đặt"
    echo "Cài đặt: brew install railway"
    exit 1
fi

# Check login
if ! railway whoami &> /dev/null; then
    echo "Đang login Railway..."
    railway login
fi

echo -e "${GREEN}✓${NC} Logged in to Railway"
echo ""

# Ask for password
echo "Nhập password cho n8n (hoặc Enter để dùng default 'admin123'):"
read -s N8N_PASSWORD
N8N_PASSWORD=${N8N_PASSWORD:-admin123}
echo ""

# Create new project for n8n
echo -e "${BLUE}[1/4]${NC} Creating Railway project for n8n..."
railway init --name vnstock-n8n

echo -e "${GREEN}✓${NC} Project created"
echo ""

# Set environment variables
echo -e "${BLUE}[2/4]${NC} Setting environment variables..."

railway variables set N8N_BASIC_AUTH_ACTIVE=true
railway variables set N8N_BASIC_AUTH_USER=admin
railway variables set N8N_BASIC_AUTH_PASSWORD="$N8N_PASSWORD"
railway variables set N8N_PORT=5678
railway variables set N8N_PROTOCOL=https
railway variables set GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
railway variables set NODE_ENV=production

echo -e "${GREEN}✓${NC} Environment variables set"
echo ""

# Create Dockerfile for n8n
echo -e "${BLUE}[3/4]${NC} Creating n8n Dockerfile..."

cat > Dockerfile.n8n << 'EOF'
FROM n8nio/n8n:latest

# Set working directory
WORKDIR /home/node

# Expose port
EXPOSE 5678

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5678/healthz || exit 1

# Start n8n
CMD ["n8n"]
EOF

echo -e "${GREEN}✓${NC} Dockerfile created"
echo ""

# Deploy
echo -e "${BLUE}[4/4]${NC} Deploying n8n to Railway..."
railway up --dockerfile Dockerfile.n8n --detach

echo -e "${GREEN}✓${NC} Deployment initiated"
echo ""

# Generate domain
echo "Generating public domain..."
sleep 3
DOMAIN=$(railway domain 2>&1 | grep -oP 'https://[^ ]+' | head -1)

if [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}✓${NC} Domain: $DOMAIN"
else
    echo "Domain generation in progress. Run 'railway domain' to get URL"
fi

echo ""
echo "═══════════════════════════════════════"
echo -e "${GREEN}🎉 n8n DEPLOYED SUCCESSFULLY!${NC}"
echo "═══════════════════════════════════════"
echo ""
echo "📊 n8n Information:"
echo "  URL:      railway domain"
echo "  Username: admin"
echo "  Password: $N8N_PASSWORD"
echo ""
echo "🔗 Connect to VNStock API:"
echo "  Trong n8n workflow, dùng HTTP Request node"
echo "  URL: https://vnstock-api-production.up.railway.app/api/..."
echo ""
echo "💡 Useful Commands:"
echo "  railway logs    # View logs"
echo "  railway open    # Open dashboard"
echo "  railway domain  # Get n8n URL"
echo ""
echo -e "${GREEN}Happy automating! 🚀${NC}"
