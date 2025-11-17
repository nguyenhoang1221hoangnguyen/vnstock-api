# ⚡ Quick Start - Deploy VNStock API lên Railway trong 5 phút

## 🎯 3 Cách Deploy (chọn 1)

### 📱 Cách 1: SIÊU NHANH - Dùng Railway Dashboard (0 dòng code)

**Bước 1:** Vào https://railway.app → Sign up bằng GitHub

**Bước 2:** Click **"New Project"** → **"Deploy from GitHub repo"**

**Bước 3:** Authorize Railway → Chọn repo `vnstock-api`

**Bước 4:** Railway tự động build và deploy!

**Bước 5:** Click **"Settings"** → **"Generate Domain"** → Nhận URL

✅ **XONG!** Truy cập: `https://vnstock-api-production.up.railway.app/docs`

---

### 💻 Cách 2: Dùng Script tự động

```bash
# Chạy 1 dòng lệnh này
./deploy-railway.sh
```

Script sẽ tự động:
- ✅ Kiểm tra Railway CLI
- ✅ Login Railway
- ✅ Setup project
- ✅ Deploy code
- ✅ Generate domain

---

### 🛠️ Cách 3: Manual với Railway CLI

```bash
# 1. Cài Railway CLI
brew install railway
# hoặc: npm i -g @railway/cli

# 2. Login
railway login

# 3. Init project
railway init

# 4. Set env variables
railway variables set API_HOST=0.0.0.0
railway variables set API_PORT=8000
railway variables set PYTHONUNBUFFERED=1
railway variables set TIMEZONE=Asia/Ho_Chi_Minh

# 5. Deploy
railway up

# 6. Generate domain
railway domain

# 7. Open dashboard
railway open
```

---

## 🎨 Environment Variables cần thiết

Trong Railway Dashboard → Variables tab, add:

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

---

## ✅ Sau khi Deploy

### 1. Kiểm tra Health
```bash
curl https://your-app.up.railway.app/health
```

### 2. Test API
```bash
# Thông tin công ty
curl https://your-app.up.railway.app/api/stock/VNM/company

# Dữ liệu giá
curl https://your-app.up.railway.app/api/stock/VNM/price?start_date=2025-01-01
```

### 3. Xem Documentation
- Swagger: `https://your-app.up.railway.app/docs`
- ReDoc: `https://your-app.up.railway.app/redoc`

---

## 📊 Xem Logs

```bash
# Real-time logs
railway logs

# hoặc vào Dashboard → Deployments → Click deployment → View logs
```

---

## 🔄 Update Code

### Auto-deploy (Khuyến nghị)

Khi deploy qua GitHub, mỗi khi push code mới:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

→ Railway tự động deploy! 🚀

### Manual deploy

```bash
railway up
```

---

## 💰 Chi phí ước tính

| Tier | Giá | RAM | Disk | Thời gian chạy |
|------|-----|-----|------|----------------|
| **Free** | $0 ($5 credit) | 512MB | 1GB | ~500h/tháng |
| **Hobby** | $5/tháng | 8GB | 100GB | Unlimited |

**Khuyến nghị:**
- Free tier: Đủ cho development và team nhỏ
- Hobby: Cho production với traffic cao

---

## 🐛 Troubleshooting

### Build failed?
```bash
# Xem logs chi tiết
railway logs --deployment

# Kiểm tra Dockerfile
docker build -t test .
```

### Service crashed?
```bash
# Restart service
railway restart

# Xem logs
railway logs
```

### Domain không hoạt động?
```bash
# Re-generate domain
railway domain
```

---

## 📚 Tài liệu đầy đủ

Xem file: `RAILWAY_DEPLOYMENT.md`

---

## 🆘 Cần trợ giúp?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Issue: https://github.com/YOUR_USERNAME/vnstock-api/issues

---

## 🎉 Đã xong!

Team của bạn giờ có thể truy cập API tại:
```
https://vnstock-api-production.up.railway.app
```

**Happy deploying! 🚀**
