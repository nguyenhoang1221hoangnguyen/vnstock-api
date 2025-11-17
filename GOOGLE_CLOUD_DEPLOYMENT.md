# ☁️ Deploy VNStock API + n8n lên Google Cloud Run

## 🎯 TẠI SAO CHỌN GOOGLE CLOUD RUN?

✅ **FREE tier cực kỳ hào phóng** (2 triệu requests/tháng)
✅ **Deploy CẢ 2 services** từ 1 docker-compose.yml
✅ **Scale tự động** 0→∞ (chỉ tính tiền khi có request)
✅ **Latency thấp** (~50ms đến VN)
✅ **$300 credit** khi đăng ký mới
✅ **Production-ready** (Google infrastructure)

---

## 💰 CHI PHÍ DỰ KIẾN

### Free Tier (Hàng tháng):
```
✅ 2,000,000 requests
✅ 360,000 GB-seconds compute
✅ 180,000 vCPU-seconds
✅ 1 GB network egress (Bắc Mỹ)
```

### Ước tính cho project của bạn:
```
Team 10 người × 50 requests/ngày:
= 15,000 requests/tháng
= $0 (FREE - chỉ 0.75% free tier)

Traffic cao (100,000 requests/tháng):
= $0.40/tháng (vẫn trong free tier)

Production (1 triệu requests/tháng):
= $2-3/tháng
```

**KẾT LUẬN: Hầu như MIỄN PHÍ cho use case của bạn!**

---

## 🚀 CÁCH 1: Deploy nhanh với Cloud Run (Khuyến nghị)

### Bước 1: Chuẩn bị Google Cloud

#### 1.1. Tạo Google Cloud Account
```
1. Vào: https://console.cloud.google.com
2. Sign up (dùng Gmail)
3. Nhận $300 credit miễn phí (valid 90 ngày)
4. Không cần credit card cho free tier
```

#### 1.2. Tạo Project mới
```
1. Vào Console: https://console.cloud.google.com
2. Click "Select a project" → "New Project"
3. Project name: vnstock-api
4. Click "Create"
```

#### 1.3. Enable APIs
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com
```

---

### Bước 2: Cài đặt Google Cloud SDK

#### macOS:
```bash
# Download và cài đặt
curl https://sdk.cloud.google.com | bash

# Restart terminal
exec -l $SHELL

# Initialize gcloud
gcloud init

# Login
gcloud auth login

# Set project
gcloud config set project vnstock-api
```

#### Verify:
```bash
gcloud --version
# google-cloud-sdk 456.0.0
```

---

### Bước 3: Chuẩn bị Docker Images

#### 3.1. Build VNStock API image
```bash
cd /Users/nguyenhoang/vnstock-api

# Build
docker build -t gcr.io/vnstock-api/vnstock-api:latest .

# Push to Google Container Registry
docker push gcr.io/vnstock-api/vnstock-api:latest
```

#### 3.2. Tạo Dockerfile cho n8n (đã tối ưu)
```dockerfile
FROM n8nio/n8n:latest

# Set working directory
WORKDIR /home/node

# Install curl for healthcheck
USER root
RUN apk add --no-cache curl
USER node

# Expose port
EXPOSE 5678

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5678/healthz || exit 1

# Start n8n
CMD ["n8n"]
```

---

### Bước 4: Deploy lên Cloud Run

#### 4.1. Deploy VNStock API
```bash
gcloud run deploy vnstock-api \
  --image gcr.io/vnstock-api/vnstock-api:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "API_HOST=0.0.0.0,API_PORT=8000,PYTHONUNBUFFERED=1,HOME=/app,VNSTOCK_DATA_DIR=/app/.vnstock,IPYTHONDIR=/app/.ipython,NODE_ENV=production,TIMEZONE=Asia/Ho_Chi_Minh"
```

**Kết quả:**
```
Service [vnstock-api] revision [vnstock-api-00001-xxx] has been deployed.
Service URL: https://vnstock-api-xxxxxxxxx-as.a.run.app
```

#### 4.2. Deploy n8n
```bash
gcloud run deploy vnstock-n8n \
  --image n8nio/n8n:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --port 5678 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars "N8N_BASIC_AUTH_ACTIVE=true,N8N_BASIC_AUTH_USER=admin,N8N_BASIC_AUTH_PASSWORD=your-secure-password,N8N_PORT=5678,N8N_PROTOCOL=https,GENERIC_TIMEZONE=Asia/Ho_Chi_Minh,NODE_ENV=production"
```

**Kết quả:**
```
Service URL: https://vnstock-n8n-xxxxxxxxx-as.a.run.app
```

---

## 🚀 CÁCH 2: Deploy tự động từ GitHub (CI/CD)

### Bước 1: Setup Cloud Build

#### 1.1. Tạo file `cloudbuild.yaml`
```yaml
steps:
  # Build VNStock API
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/vnstock-api', '.']

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/vnstock-api']

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'vnstock-api'
      - '--image=gcr.io/$PROJECT_ID/vnstock-api'
      - '--region=asia-southeast1'
      - '--platform=managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/vnstock-api'
```

#### 1.2. Connect GitHub Repository
```bash
# Trong Google Cloud Console:
1. Vào Cloud Build → Triggers
2. Click "Connect Repository"
3. Chọn GitHub
4. Authorize Google Cloud
5. Chọn repo: nguyenhoang1221hoangnguyen/vnstock-api
6. Create Trigger:
   - Name: deploy-on-push
   - Event: Push to main branch
   - Configuration: cloudbuild.yaml
```

**Kết quả:**
- Mỗi khi push code lên GitHub → Tự động deploy!

---

## 🚀 CÁCH 3: Deploy bằng Script tự động (NHANH NHẤT)

Tôi sẽ tạo script tự động cho bạn ở phần sau...

---

## 📊 SAU KHI DEPLOY

### Your services sẽ có URLs:

```
VNStock API: https://vnstock-api-xxxxxxxxx-as.a.run.app
n8n:         https://vnstock-n8n-xxxxxxxxx-as.a.run.app

API Docs:    https://vnstock-api-xxxxxxxxx-as.a.run.app/docs
n8n Login:   https://vnstock-n8n-xxxxxxxxx-as.a.run.app
```

### Test API:
```bash
# Health check
curl https://vnstock-api-xxxxxxxxx-as.a.run.app/health

# Company info
curl https://vnstock-api-xxxxxxxxx-as.a.run.app/api/stock/VNM/company
```

---

## 🔧 QUẢN LÝ SAU KHI DEPLOY

### Xem logs:
```bash
# VNStock API logs
gcloud run logs read vnstock-api --region asia-southeast1 --limit 50

# n8n logs
gcloud run logs read vnstock-n8n --region asia-southeast1 --limit 50

# Real-time logs
gcloud run logs tail vnstock-api --region asia-southeast1
```

### Xem metrics:
```bash
# Vào Console
https://console.cloud.google.com/run

# Chọn service → Tab "Metrics"
# Xem: Requests, Latency, Memory, CPU
```

### Update service:
```bash
# Build image mới
docker build -t gcr.io/vnstock-api/vnstock-api:v2 .
docker push gcr.io/vnstock-api/vnstock-api:v2

# Deploy version mới
gcloud run deploy vnstock-api \
  --image gcr.io/vnstock-api/vnstock-api:v2 \
  --region asia-southeast1
```

### Scale service:
```bash
# Tăng max instances
gcloud run services update vnstock-api \
  --max-instances 20 \
  --region asia-southeast1

# Set min instances (always-on, tốn tiền hơn)
gcloud run services update vnstock-api \
  --min-instances 1 \
  --region asia-southeast1
```

---

## 🌐 CUSTOM DOMAIN

### Bước 1: Verify domain ownership
```bash
gcloud domains verify yourdomain.com
```

### Bước 2: Map domain
```bash
gcloud run domain-mappings create \
  --service vnstock-api \
  --domain api.yourdomain.com \
  --region asia-southeast1
```

### Bước 3: Update DNS
```
Thêm CNAME record:
api.yourdomain.com → ghs.googlehosted.com
```

**Kết quả:**
```
VNStock API: https://api.yourdomain.com
n8n:         https://n8n.yourdomain.com
```

---

## 💾 THÊM DATABASE (Optional)

### Cloud SQL (PostgreSQL):
```bash
# Tạo Cloud SQL instance
gcloud sql instances create vnstock-db \
  --database-version=POSTGRES_14 \
  --cpu=1 \
  --memory=3.75GB \
  --region=asia-southeast1 \
  --root-password=your-password

# Connect với Cloud Run
gcloud run services update vnstock-api \
  --add-cloudsql-instances vnstock-db \
  --region asia-southeast1

# Set DATABASE_URL
gcloud run services update vnstock-api \
  --set-env-vars "DATABASE_URL=postgresql://..." \
  --region asia-southeast1
```

**Chi phí:**
- Cloud SQL: ~$10-25/tháng (db-f1-micro)

---

## 🔐 BẢO MẬT

### 1. IAM & Authentication
```bash
# Tắt public access (require auth)
gcloud run services update vnstock-api \
  --no-allow-unauthenticated \
  --region asia-southeast1

# Tạo service account
gcloud iam service-accounts create vnstock-api-sa

# Grant permissions
gcloud run services add-iam-policy-binding vnstock-api \
  --member="serviceAccount:vnstock-api-sa@project-id.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region asia-southeast1
```

### 2. Secrets Management
```bash
# Store secrets in Secret Manager
echo "your-api-key" | gcloud secrets create vnstock-api-key --data-file=-

# Use in Cloud Run
gcloud run services update vnstock-api \
  --update-secrets=API_KEY=vnstock-api-key:latest \
  --region asia-southeast1
```

---

## 📊 MONITORING & ALERTS

### 1. Setup Alerting
```bash
# Vào Cloud Console
# Monitoring → Alerting → Create Policy

# Alert conditions:
- Latency > 1000ms
- Error rate > 5%
- CPU > 80%
- Memory > 90%

# Notification channels:
- Email
- Slack
- SMS
```

### 2. Dashboard
```
Cloud Console → Monitoring → Dashboards

Metrics:
- Request count
- Request latency
- Error rate
- CPU utilization
- Memory utilization
- Container instance count
```

---

## 💰 COST OPTIMIZATION

### 1. Set budget alerts
```bash
# Vào Billing → Budgets & alerts
# Set budget: $10/tháng
# Alert at: 50%, 90%, 100%
```

### 2. Optimize resources
```bash
# Giảm memory nếu không cần
gcloud run services update vnstock-api \
  --memory 256Mi \
  --region asia-southeast1

# Set request timeout
gcloud run services update vnstock-api \
  --timeout 60s \
  --region asia-southeast1

# Set concurrency
gcloud run services update vnstock-api \
  --concurrency 80 \
  --region asia-southeast1
```

### 3. Enable container startup optimization
```bash
gcloud run services update vnstock-api \
  --cpu-throttling \
  --region asia-southeast1
```

---

## 🔄 CI/CD với GitHub Actions

File `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v0
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: vnstock-api

    - name: Build and Push
      run: |
        gcloud builds submit --tag gcr.io/vnstock-api/vnstock-api

    - name: Deploy
      run: |
        gcloud run deploy vnstock-api \
          --image gcr.io/vnstock-api/vnstock-api \
          --region asia-southeast1 \
          --platform managed
```

---

## 🐛 TROUBLESHOOTING

### Service không start:
```bash
# Xem logs chi tiết
gcloud run logs read vnstock-api --region asia-southeast1 --limit 100

# Common issues:
- Port mismatch (phải match với PORT env var)
- Memory limit quá thấp
- Health check fail
```

### Slow cold start:
```bash
# Set min-instances = 1 (always warm)
gcloud run services update vnstock-api \
  --min-instances 1 \
  --region asia-southeast1

# Chi phí: ~$5-10/tháng thêm
```

### High latency:
```bash
# Chọn region gần user hơn
--region asia-southeast1  # Singapore (tốt cho VN)

# Tăng CPU
--cpu 2

# Tăng concurrency
--concurrency 100
```

---

## ✅ CHECKLIST

- [ ] Tạo Google Cloud account
- [ ] Nhận $300 credit
- [ ] Enable APIs (Cloud Run, Container Registry, Cloud Build)
- [ ] Cài gcloud CLI
- [ ] Build Docker images
- [ ] Deploy VNStock API
- [ ] Deploy n8n
- [ ] Test endpoints
- [ ] Setup custom domain (optional)
- [ ] Setup monitoring
- [ ] Setup budget alerts
- [ ] Setup CI/CD (optional)

---

## 📞 HỖ TRỢ

- Google Cloud Docs: https://cloud.google.com/run/docs
- Cloud Run Quickstart: https://cloud.google.com/run/docs/quickstarts
- Pricing Calculator: https://cloud.google.com/products/calculator

---

## 🎉 TÓM TẮT

**Google Cloud Run là lựa chọn TỐT NHẤT vì:**

✅ FREE tier hào phóng (2M requests/tháng)
✅ Deploy CẢ 2 services dễ dàng
✅ Auto-scaling 0→∞
✅ Chi phí thực tế: $0-5/tháng
✅ Production-ready (Google infrastructure)
✅ $300 credit miễn phí khi đăng ký

**Chi phí dự kiến:**
- Team nhỏ (< 100k req/tháng): **$0 (FREE)**
- Production (1M req/tháng): **$2-3/tháng**
- High traffic (5M req/tháng): **$10-15/tháng**

**→ RẺ HƠN Railway, DigitalOcean, và hầu hết các nền tảng khác!**
