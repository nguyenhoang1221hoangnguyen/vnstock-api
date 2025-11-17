#!/bin/bash

# Deploy VNStock API + n8n to Google Cloud Run
# Usage: ./deploy-google-cloud.sh

set -e

echo "☁️  Deploy to Google Cloud Run"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="vnstock-api"
REGION="asia-southeast1"  # Singapore - closest to Vietnam
REGISTRY="gcr.io"

echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION (Singapore)"
echo "  Registry: $REGISTRY"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗${NC} gcloud CLI chưa được cài đặt"
    echo ""
    echo "Cài đặt gcloud CLI:"
    echo "  macOS: curl https://sdk.cloud.google.com | bash"
    echo "  Hoặc xem: https://cloud.google.com/sdk/docs/install"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} gcloud CLI installed ($(gcloud --version | head -1))"
echo ""

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Chưa đăng nhập Google Cloud"
    echo ""
    read -p "Login ngay bây giờ? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud auth login
    else
        echo "Vui lòng login trước: gcloud auth login"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} Logged in as: $(gcloud auth list --filter=status:ACTIVE --format="value(account)")"
echo ""

# Check/Create project
echo -e "${BLUE}[1/7]${NC} Checking Google Cloud project..."

if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Project '$PROJECT_ID' không tồn tại"
    read -p "Tạo project mới? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud projects create $PROJECT_ID --name="VNStock API"
        echo -e "${GREEN}✓${NC} Project created"
    else
        echo "Vui lòng tạo project trước hoặc chỉnh sửa PROJECT_ID trong script"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Project '$PROJECT_ID' exists"
fi

# Set current project
gcloud config set project $PROJECT_ID
echo ""

# Enable APIs
echo -e "${BLUE}[2/7]${NC} Enabling required APIs..."

apis=(
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "cloudbuild.googleapis.com"
)

for api in "${apis[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo -e "${GREEN}✓${NC} $api already enabled"
    else
        echo "Enabling $api..."
        gcloud services enable $api
        echo -e "${GREEN}✓${NC} $api enabled"
    fi
done
echo ""

# Build VNStock API
echo -e "${BLUE}[3/7]${NC} Building VNStock API Docker image..."

IMAGE_API="$REGISTRY/$PROJECT_ID/vnstock-api:latest"

echo "Building image: $IMAGE_API"
docker build -t $IMAGE_API . || {
    echo -e "${RED}✗${NC} Build failed"
    exit 1
}

echo -e "${GREEN}✓${NC} VNStock API image built"
echo ""

# Push to Container Registry
echo -e "${BLUE}[4/7]${NC} Pushing images to Container Registry..."

# Configure docker for gcloud
gcloud auth configure-docker --quiet

echo "Pushing VNStock API..."
docker push $IMAGE_API

echo -e "${GREEN}✓${NC} Images pushed to registry"
echo ""

# Get n8n password
echo -e "${BLUE}[5/7]${NC} Setup n8n credentials..."
echo ""
echo "Nhập password cho n8n (hoặc Enter để dùng mặc định 'admin123'):"
read -s N8N_PASSWORD
N8N_PASSWORD=${N8N_PASSWORD:-admin123}
echo ""
echo -e "${GREEN}✓${NC} n8n password set"
echo ""

# Deploy VNStock API
echo -e "${BLUE}[6/7]${NC} Deploying VNStock API to Cloud Run..."

gcloud run deploy vnstock-api \
  --image $IMAGE_API \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars "API_HOST=0.0.0.0,API_PORT=8000,PYTHONUNBUFFERED=1,HOME=/app,VNSTOCK_DATA_DIR=/app/.vnstock,IPYTHONDIR=/app/.ipython,NODE_ENV=production,TIMEZONE=Asia/Ho_Chi_Minh" \
  --quiet

API_URL=$(gcloud run services describe vnstock-api --region $REGION --format="value(status.url)")
echo -e "${GREEN}✓${NC} VNStock API deployed: $API_URL"
echo ""

# Deploy n8n
echo -e "${BLUE}[7/7]${NC} Deploying n8n to Cloud Run..."

gcloud run deploy vnstock-n8n \
  --image n8nio/n8n:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 5678 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 300 \
  --set-env-vars "N8N_BASIC_AUTH_ACTIVE=true,N8N_BASIC_AUTH_USER=admin,N8N_BASIC_AUTH_PASSWORD=$N8N_PASSWORD,N8N_PORT=5678,N8N_PROTOCOL=https,GENERIC_TIMEZONE=Asia/Ho_Chi_Minh,NODE_ENV=production,WEBHOOK_URL=https://vnstock-n8n-$PROJECT_ID.a.run.app/" \
  --quiet

N8N_URL=$(gcloud run services describe vnstock-n8n --region $REGION --format="value(status.url)")
echo -e "${GREEN}✓${NC} n8n deployed: $N8N_URL"
echo ""

# Summary
echo "═══════════════════════════════════════════════════"
echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
echo "═══════════════════════════════════════════════════"
echo ""
echo "📊 Deployment Summary:"
echo "  ✓ Google Cloud Project: $PROJECT_ID"
echo "  ✓ Region: $REGION (Singapore)"
echo "  ✓ APIs Enabled: Cloud Run, Container Registry, Cloud Build"
echo "  ✓ VNStock API deployed"
echo "  ✓ n8n deployed"
echo ""
echo "🌐 Service URLs:"
echo "  VNStock API: $API_URL"
echo "  n8n:         $N8N_URL"
echo ""
echo "📖 API Documentation:"
echo "  Swagger UI:  $API_URL/docs"
echo "  ReDoc:       $API_URL/redoc"
echo ""
echo "🔐 n8n Credentials:"
echo "  URL:      $N8N_URL"
echo "  Username: admin"
echo "  Password: $N8N_PASSWORD"
echo ""
echo "💡 Next Steps:"
echo "  1. Test API:        curl $API_URL/health"
echo "  2. View logs:       gcloud run logs tail vnstock-api --region $REGION"
echo "  3. Open n8n:        open $N8N_URL"
echo "  4. View dashboard:  gcloud run services list"
echo "  5. Monitor:         https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""
echo "💰 Cost Estimate:"
echo "  Free tier: 2 million requests/month"
echo "  Your usage: ~\$0-5/month (hầu như miễn phí)"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs:      gcloud run logs read vnstock-api --region $REGION"
echo "  Update service: gcloud run deploy vnstock-api --image $IMAGE_API --region $REGION"
echo "  Delete service: gcloud run services delete vnstock-api --region $REGION"
echo "  View metrics:   https://console.cloud.google.com/run"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
