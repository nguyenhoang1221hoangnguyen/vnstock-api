# 🚀 HƯỚNG DẪN DEPLOY - THỰC HIỆN NGAY

## ✅ Đã hoàn thành (Tự động):

1. ✅ **Git repository** đã init
2. ✅ **Code đã push** lên https://github.com/nguyenhoang1221hoangnguyen/vnstock-api.git
3. ✅ **Railway CLI** đã cài đặt (v4.11.1)
4. ✅ **vnstock v3.3.0** upgraded và tested
5. ✅ **Deployment scripts** đã tạo sẵn

---

## 🎯 BẠN CHỈ CẦN CHẠY 5 LỆNH SAU:

### Mở Terminal và chạy:

```bash
# 1. Di chuyển vào thư mục project
cd /Users/nguyenhoang/vnstock-api

# 2. Login Railway (browser sẽ mở)
railway login
```

**→ Browser sẽ mở, đăng nhập Railway:**
- Nếu chưa có tài khoản: Sign up tại https://railway.app
- Login bằng GitHub (khuyến nghị) hoặc email
- Authorize Railway CLI

```bash
# 3. Tạo project mới
railway init --name vnstock-api
```

**→ Chọn:** "Empty Project"

```bash
# 4. Set environment variables
railway variables set API_HOST=0.0.0.0 API_PORT=8000 PYTHONUNBUFFERED=1 HOME=/app VNSTOCK_DATA_DIR=/app/.vnstock IPYTHONDIR=/app/.ipython NODE_ENV=production TIMEZONE=Asia/Ho_Chi_Minh

# 5. Deploy!
railway up
```

**→ Đợi 2-3 phút để Railway build Docker image**

```bash
# 6. Lấy URL public
railway domain
```

**✅ XONG! API đã live!**

---

## 📱 Hoặc dùng Script Tự động:

```bash
cd /Users/nguyenhoang/vnstock-api
./deploy-now.sh
```

Script sẽ tự động làm tất cả các bước trên!

---

## 🌐 Sau khi Deploy:

### Test API:

```bash
# Get domain
DOMAIN=$(railway domain)

# Health check
curl $DOMAIN/health

# Company info
curl $DOMAIN/api/stock/VNM/company

# API Documentation
open $DOMAIN/docs
```

### Share với team:

```
API URL: https://vnstock-api-production.up.railway.app
API Docs: https://vnstock-api-production.up.railway.app/docs
```

---

## 📊 Monitoring:

```bash
# Xem logs real-time
railway logs

# Xem status
railway status

# Mở dashboard
railway open

# Restart service
railway restart
```

---

## 🔄 Update Code sau này:

Mỗi khi update code, chỉ cần:

```bash
git add .
git commit -m "Update feature"
git push origin main

# Sau đó deploy
railway up
```

Hoặc setup auto-deploy từ GitHub (trong Railway dashboard)!

---

## 💰 Chi phí:

- **Free tier**: $5 credit/tháng
- **Đủ cho**: ~500 giờ runtime
- **RAM**: 512MB
- **Bandwidth**: Unlimited

→ **Hoàn toàn đủ cho team nhỏ (5-10 người)**

---

## 🆘 Nếu gặp lỗi:

### Build failed:
```bash
railway logs --deployment
```

### Service crashed:
```bash
railway restart
railway logs
```

### Domain không work:
```bash
railway domain --generate
```

---

## 🎉 Checklist:

- [ ] Railway login thành công
- [ ] Project được tạo
- [ ] Environment variables đã set
- [ ] Deploy thành công
- [ ] Domain đã generate
- [ ] Test /health endpoint
- [ ] Test /docs endpoint
- [ ] Share URL với team

---

## 📞 Support:

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/nguyenhoang1221hoangnguyen/vnstock-api/issues

---

## ⚡ QUICK START - Copy & Paste:

```bash
cd /Users/nguyenhoang/vnstock-api
railway login
railway init --name vnstock-api
railway variables set API_HOST=0.0.0.0 API_PORT=8000 PYTHONUNBUFFERED=1 HOME=/app VNSTOCK_DATA_DIR=/app/.vnstock IPYTHONDIR=/app/.ipython NODE_ENV=production TIMEZONE=Asia/Ho_Chi_Minh
railway up
railway domain
railway logs
```

**Thời gian: 3-5 phút**

**Happy deploying! 🚀**
