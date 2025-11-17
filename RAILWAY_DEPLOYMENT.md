# 🚀 Hướng dẫn Deploy VNStock API lên Railway

## 📋 Mục lục
1. [Chuẩn bị](#chuẩn-bị)
2. [Deploy bằng Railway CLI](#deploy-bằng-railway-cli)
3. [Deploy bằng GitHub](#deploy-bằng-github)
4. [Cấu hình sau khi deploy](#cấu-hình-sau-khi-deploy)
5. [Monitoring và Logs](#monitoring-và-logs)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Chuẩn bị

### 1. Tạo tài khoản Railway
- Truy cập: https://railway.app
- Sign up bằng GitHub (khuyến nghị)
- Nhận $5 credit miễn phí mỗi tháng

### 2. Cài đặt Railway CLI (Tùy chọn)
```bash
# macOS
brew install railway

# hoặc dùng npm
npm i -g @railway/cli

# Verify
railway --version
```

---

## 🚀 PHƯƠNG PHÁP 1: Deploy bằng Railway CLI (Nhanh nhất)

### Bước 1: Khởi tạo Git (nếu chưa có)
```bash
cd /Users/nguyenhoang/vnstock-api

# Khởi tạo git
git init

# Tạo .gitignore nếu chưa có
git add .
git commit -m "Initial commit - VNStock API v3.3.0"
```

### Bước 2: Login Railway
```bash
railway login
```
→ Browser sẽ mở, đăng nhập và authorize

### Bước 3: Khởi tạo project
```bash
# Tạo project mới
railway init

# Chọn "Empty Project"
# Đặt tên: vnstock-api (hoặc tên bạn muốn)
```

### Bước 4: Deploy
```bash
# Deploy lần đầu
railway up

# Theo dõi logs
railway logs
```

### Bước 5: Lấy public URL
```bash
# Generate domain
railway domain

# Hoặc vào dashboard
railway open
```

✅ **Xong!** API của bạn đã live tại: `https://vnstock-api.up.railway.app`

---

## 🐙 PHƯƠNG PHÁP 2: Deploy bằng GitHub (Khuyến nghị cho team)

### Bước 1: Push code lên GitHub

#### 1.1. Tạo repository trên GitHub
- Vào https://github.com/new
- Tên repo: `vnstock-api`
- Chọn Private hoặc Public
- **KHÔNG** chọn "Initialize with README"

#### 1.2. Push code
```bash
cd /Users/nguyenhoang/vnstock-api

# Init git (nếu chưa có)
git init
git add .
git commit -m "Initial commit - VNStock API v3.3.0"

# Add remote (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/vnstock-api.git

# Push
git branch -M main
git push -u origin main
```

### Bước 2: Deploy từ Railway Dashboard

1. Vào https://railway.app/dashboard
2. Click **"New Project"**
3. Chọn **"Deploy from GitHub repo"**
4. Authorize Railway truy cập GitHub
5. Chọn repository `vnstock-api`
6. Railway sẽ tự động:
   - Detect Dockerfile
   - Build Docker image
   - Deploy service
   - Generate public URL

### Bước 3: Configure Environment Variables

Trong Railway dashboard:
1. Click vào service `vnstock-api`
2. Tab **"Variables"**
3. Add các biến sau:

```bash
API_HOST=0.0.0.0
API_PORT=8000
PYTHONUNBUFFERED=1
HOME=/app
VNSTOCK_DATA_DIR=/app/.vnstock
IPYTHONDIR=/app/.ipython
NODE_ENV=production
TIMEZONE=Asia/Ho_Chi_Minh
```

4. Click **"Deploy"** để apply changes

### Bước 4: Setup Custom Domain (Tùy chọn)

1. Tab **"Settings"**
2. Section **"Domains"**
3. Click **"Generate Domain"** → Nhận domain: `*.up.railway.app`
4. Hoặc add custom domain của bạn

---

## ⚙️ Cấu hình sau khi deploy

### 1. Kiểm tra Health
```bash
curl https://your-app.up.railway.app/health
```

Kết quả mong đợi:
```json
{"status":"healthy","service":"vnstock-api"}
```

### 2. Test API
```bash
# Lấy thông tin công ty
curl https://your-app.up.railway.app/api/stock/VNM/company

# Lấy dữ liệu giá
curl https://your-app.up.railway.app/api/stock/VNM/price?start_date=2025-01-01&end_date=2025-01-10
```

### 3. Truy cập API Docs
- Swagger UI: `https://your-app.up.railway.app/docs`
- ReDoc: `https://your-app.up.railway.app/redoc`

### 4. Thêm Database (Nếu cần)

Railway có PostgreSQL, MySQL, Redis miễn phí:

1. Click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway tự động tạo biến `DATABASE_URL`
3. Update code để dùng PostgreSQL thay vì SQLite

---

## 📊 Monitoring và Logs

### Xem Logs
```bash
# CLI
railway logs

# hoặc vào Dashboard → Service → Tab "Deployments" → Click deployment → View logs
```

### Metrics
- Dashboard → Service → Tab "Metrics"
- Xem: CPU, Memory, Network usage

### Alerts
- Settings → Notifications
- Nhận alert qua Email/Slack khi service down

---

## 🎛️ Deploy n8n cùng Railway (Bonus)

Nếu muốn deploy cả n8n workflow:

### Cách 1: Separate Service

1. **New Project** trong Railway
2. **Deploy from Docker Image**: `n8nio/n8n:latest`
3. Add biến môi trường:
```bash
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password
N8N_HOST=your-n8n.up.railway.app
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://your-n8n.up.railway.app/
GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
```

4. Add Volume cho persistent data:
   - Path: `/home/node/.n8n`

### Cách 2: Monorepo (Advanced)

Dùng Railway's multi-service trong 1 repo với `railway.toml`

---

## 🔧 CI/CD tự động

Railway tự động deploy khi:
- ✅ Push code lên GitHub (main branch)
- ✅ Merge Pull Request
- ✅ Create new Release/Tag

### Customize deployment:

Tạo file `railway.toml`:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
numReplicas = 1
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/health"
healthcheckTimeout = 100
```

---

## 🐛 Troubleshooting

### 1. Build failed
**Lỗi:** `Failed to build Docker image`

**Giải pháp:**
- Kiểm tra Dockerfile syntax
- Đảm bảo requirements.txt đúng
- Xem logs chi tiết trong Railway dashboard

### 2. Service crashed
**Lỗi:** `Application failed to respond`

**Giải pháp:**
```bash
# Xem logs
railway logs

# Thường do:
# - Port không đúng (phải dùng $PORT hoặc 8000)
# - Missing environment variables
# - Database connection failed
```

### 3. Out of memory
**Lỗi:** `OOMKilled`

**Giải pháp:**
- Upgrade Railway plan (free tier: 512MB RAM)
- Optimize code (giảm memory usage)
- Add swap space trong Dockerfile

### 4. Slow cold start
**Vấn đề:** Lần đầu tiên truy cập chậm

**Giải pháp:**
- Railway free tier sleep sau 10 phút không dùng
- Upgrade lên Hobby plan ($5/tháng) để always on
- Hoặc dùng cron job ping health endpoint mỗi 5 phút

---

## 💰 Chi phí

### Free Tier
- **$5 credit/tháng**
- ~500 giờ chạy/tháng
- 512MB RAM
- 1GB disk
- **Đủ cho team nhỏ (5-10 người)**

### Hobby Plan
- **$5/tháng** (unlimited)
- 8GB RAM
- 100GB disk
- Always-on
- **Khuyến nghị cho production**

### Ước tính:
- API chạy 24/7: ~$5-10/tháng
- API + n8n: ~$10-15/tháng
- API + n8n + PostgreSQL: ~$15-20/tháng

---

## 📞 Hỗ trợ

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- VNStock Docs: https://vnstocks.com/docs

---

## ✅ Checklist Deploy

- [ ] Tạo tài khoản Railway
- [ ] Push code lên GitHub
- [ ] Connect repo với Railway
- [ ] Configure environment variables
- [ ] Generate public domain
- [ ] Test API endpoints
- [ ] Setup monitoring/alerts
- [ ] Share URL với team
- [ ] (Optional) Add custom domain
- [ ] (Optional) Deploy n8n

---

## 🎉 Xong!

API của bạn đã sẵn sàng cho team sử dụng tại:
```
https://vnstock-api.up.railway.app
```

API Documentation:
```
https://vnstock-api.up.railway.app/docs
```

**Happy coding! 🚀**
