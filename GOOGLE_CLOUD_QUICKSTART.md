# ⚡ Google Cloud Run - Quick Start (5 phút)

## ✅ HOÀN THÀNH: gcloud CLI đã cài đặt!

```
Google Cloud SDK 547.0.0 ✓
```

---

## 🚀 DEPLOY NGAY BÂY GIỜ - 4 BƯỚC:

### **BƯỚC 1: Setup gcloud path**

```bash
# Add to your shell profile (chạy 1 lần)
echo 'export PATH="$HOME/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Hoặc chỉ cho session hiện tại:
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
```

---

### **BƯỚC 2: Login Google Cloud**

```bash
# Login (browser sẽ mở)
gcloud auth login

# Authorize trên browser
# → Chọn Google account
# → Click "Allow"
```

---

### **BƯỚC 3: Tạo & Setup Project**

```bash
# Set project ID
PROJECT_ID="vnstock-api-$(date +%s)"

# Tạo project
gcloud projects create $PROJECT_ID --name="VNStock API"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (cần để dùng Cloud Run)
# Vào: https://console.cloud.google.com/billing
# Link billing account với project

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

### **BƯỚC 4: Deploy Services**

#### 4.1. Deploy VNStock API

```bash
cd /Users/nguyenhoang/vnstock-api

# Build image bằng Cloud Build (không cần Docker local)
gcloud builds submit --tag gcr.io/$PROJECT_ID/vnstock-api

# Deploy to Cloud Run
gcloud run deploy vnstock-api \
  --image gcr.io/$PROJECT_ID/vnstock-api \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --set-env-vars "API_HOST=0.0.0.0,API_PORT=8000,PYTHONUNBUFFERED=1,HOME=/app,NODE_ENV=production,TIMEZONE=Asia/Ho_Chi_Minh"
```

**Kết quả:**
```
Service URL: https://vnstock-api-xxxxx-as.a.run.app
```

#### 4.2. Deploy n8n

```bash
# Deploy n8n (từ Docker Hub)
gcloud run deploy vnstock-n8n \
  --image n8nio/n8n:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --port 5678 \
  --memory 512Mi \
  --set-env-vars "N8N_BASIC_AUTH_ACTIVE=true,N8N_BASIC_AUTH_USER=admin,N8N_BASIC_AUTH_PASSWORD=your-password,N8N_PORT=5678,N8N_PROTOCOL=https,NODE_ENV=production"
```

**Kết quả:**
```
Service URL: https://vnstock-n8n-xxxxx-as.a.run.app
```

---

## ✅ XONG! Test ngay:

```bash
# Get API URL
API_URL=$(gcloud run services describe vnstock-api --region asia-southeast1 --format="value(status.url)")

# Test health
curl $API_URL/health

# Test API
curl $API_URL/api/stock/VNM/company

# Open docs
open $API_URL/docs

# Get n8n URL
N8N_URL=$(gcloud run services describe vnstock-n8n --region asia-southeast1 --format="value(status.url)")

# Open n8n
open $N8N_URL
```

---

## 💰 CHI PHÍ:

**Free Tier:**
- 2 triệu requests/tháng = FREE
- Team 10 người ≈ 15k requests/tháng = **$0**

**$300 Credit miễn phí:**
- Khi đăng ký mới
- Dùng được 3-6 tháng

---

## 🔧 QUẢN LÝ:

### Xem logs:
```bash
gcloud run logs tail vnstock-api --region asia-southeast1
```

### Xem services:
```bash
gcloud run services list
```

### Update service:
```bash
# Build image mới
gcloud builds submit --tag gcr.io/$PROJECT_ID/vnstock-api:v2

# Deploy
gcloud run deploy vnstock-api \
  --image gcr.io/$PROJECT_ID/vnstock-api:v2 \
  --region asia-southeast1
```

### Dashboard:
```
https://console.cloud.google.com/run
```

---

## 🐛 TROUBLESHOOTING:

### Billing chưa enable?
```
Vào: https://console.cloud.google.com/billing
Click "Link a billing account"
```

### Build failed?
```bash
# Xem logs
gcloud builds log --stream

# Check Dockerfile
docker build -t test .
```

### Permission denied?
```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

---

## 📞 HỖ TRỢ:

- Console: https://console.cloud.google.com
- Docs: https://cloud.google.com/run/docs
- Support: https://cloud.google.com/support

---

## ✨ TÓM TẮT:

**✅ gcloud CLI installed**
**✅ Ready to deploy**

**Next:**
1. `gcloud auth login`
2. Create project
3. Deploy VNStock API
4. Deploy n8n
5. Done! 🎉

**Thời gian: 5-10 phút**
**Chi phí: $0-5/tháng**

**Happy deploying! 🚀**
