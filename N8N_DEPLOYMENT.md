# 🔧 Deploy n8n lên Railway

## 📊 Tình trạng hiện tại:

✅ **n8n đã được cấu hình trong project:**
- Docker Compose: Có service n8n
- Local access: http://localhost:5678
- Username: `admin`
- Password: `admin123`
- Đang chạy: Container n8n (Up 6 hours)

---

## 🚀 3 CÁCH DEPLOY N8N LÊN RAILWAY:

### ⚡ **CÁCH 1: Script Tự động** (Khuyến nghị - Nhanh nhất)

```bash
cd /Users/nguyenhoang/vnstock-api
./deploy-n8n-railway.sh
```

**Script sẽ tự động:**
1. ✅ Tạo Railway project riêng cho n8n
2. ✅ Set environment variables
3. ✅ Deploy n8n container
4. ✅ Generate public domain
5. ✅ Show credentials để login

**Thời gian:** ~3 phút

---

### 💻 **CÁCH 2: Manual với Railway CLI**

```bash
# 1. Login Railway (nếu chưa)
railway login

# 2. Tạo project mới cho n8n
railway init --name vnstock-n8n

# 3. Set environment variables
railway variables set \
  N8N_BASIC_AUTH_ACTIVE=true \
  N8N_BASIC_AUTH_USER=admin \
  N8N_BASIC_AUTH_PASSWORD=your-secure-password \
  N8N_PORT=5678 \
  N8N_PROTOCOL=https \
  GENERIC_TIMEZONE=Asia/Ho_Chi_Minh \
  NODE_ENV=production

# 4. Tạo Dockerfile cho n8n
cat > Dockerfile.n8n << 'EOF'
FROM n8nio/n8n:latest
WORKDIR /home/node
EXPOSE 5678
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5678/healthz || exit 1
CMD ["n8n"]
EOF

# 5. Deploy
railway up --dockerfile Dockerfile.n8n

# 6. Get domain
railway domain
```

---

### 🌐 **CÁCH 3: Railway Dashboard** (GUI - Dễ nhất)

1. **Vào:** https://railway.app/dashboard

2. **Click:** "New Project"

3. **Chọn:** "Deploy Docker Image"

4. **Nhập:** `n8nio/n8n:latest`

5. **Add Variables** (Tab "Variables"):
   ```
   N8N_BASIC_AUTH_ACTIVE=true
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=your-password
   N8N_PORT=5678
   N8N_PROTOCOL=https
   GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
   ```

6. **Generate Domain:** Settings → Domains → Generate Domain

7. **✅ Done!** Truy cập n8n tại domain vừa tạo

---

## 🔗 Kết nối n8n với VNStock API:

Sau khi cả 2 services đã deploy:

### 1. Trong n8n Workflow:

**HTTP Request Node:**
```
Method: GET
URL: https://vnstock-api-production.up.railway.app/api/stock/VNM/company
Authentication: None
```

### 2. Example Workflow: Lấy dữ liệu stock tự động

```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 1
            }
          ]
        }
      }
    },
    {
      "name": "Get Stock Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "https://vnstock-api-production.up.railway.app/api/stock/VNM/company"
      }
    },
    {
      "name": "Send to Slack/Email",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "text": "Stock VNM: {{$json}}"
      }
    }
  ]
}
```

---

## 📊 Sau khi Deploy:

### URLs:

```
VNStock API: https://vnstock-api-production.up.railway.app
n8n:         https://vnstock-n8n-production.up.railway.app

API Docs:    https://vnstock-api-production.up.railway.app/docs
n8n Login:   https://vnstock-n8n-production.up.railway.app
```

### Credentials:

```
n8n Username: admin
n8n Password: [your-password]
```

---

## 🔐 Bảo mật:

### QUAN TRỌNG - Đổi password mặc định:

```bash
# Trong Railway dashboard của n8n:
# Variables → Edit N8N_BASIC_AUTH_PASSWORD
# Hoặc dùng CLI:

railway variables set N8N_BASIC_AUTH_PASSWORD=new-secure-password
railway restart
```

### Tạo password mạnh:
```bash
# Generate random password
openssl rand -base64 24
```

---

## 💰 Chi phí:

### Railway Free Tier:

**Option 1: Deploy cả 2 trong cùng account**
- VNStock API: ~$2.5/tháng (~250h)
- n8n: ~$2.5/tháng (~250h)
- **Total: $5 credit/tháng (FREE)**

**Option 2: Mỗi service 1 Railway account**
- Account 1 (VNStock API): $5 credit
- Account 2 (n8n): $5 credit
- **Total: $10 credit/tháng (2 accounts FREE)**

### Nếu cần thêm:
- **Hobby Plan**: $5/tháng/service
- Unlimited usage
- 8GB RAM
- 100GB disk

---

## 📱 Use Cases với n8n + VNStock API:

### 1. **Stock Alert Bot**
- Trigger: Mỗi 5 phút
- Get stock price
- If price > threshold → Send Telegram/Slack alert

### 2. **Daily Stock Report**
- Trigger: 9:00 AM mỗi ngày
- Get multiple stocks data
- Generate report
- Send email với Excel/PDF

### 3. **Portfolio Monitoring**
- Trigger: Every hour
- Get portfolio analytics
- Calculate P&L
- Update Google Sheets

### 4. **Market Screener**
- Trigger: Daily
- Scan market for opportunities
- Filter by PE, ROE, etc.
- Send top picks to Slack

### 5. **Price Change Notification**
- Trigger: Every 15 minutes
- Check price change > 5%
- Send push notification
- Save to database

---

## 🛠️ Monitoring:

### n8n Logs:
```bash
railway logs
```

### n8n Dashboard:
```bash
railway open
```

### n8n Health:
```bash
curl https://your-n8n-domain.up.railway.app/healthz
```

---

## 🔄 Update n8n:

Railway tự động pull latest n8n image. Để force update:

```bash
railway restart
```

Hoặc trong dashboard: Deployments → Redeploy

---

## 🐛 Troubleshooting:

### n8n không start:
```bash
railway logs
# Check environment variables
railway variables
```

### Cannot connect to VNStock API:
```bash
# Test API từ n8n container
curl https://vnstock-api-production.up.railway.app/health

# Verify cả 2 services đều running
```

### Forgot password:
```bash
railway variables set N8N_BASIC_AUTH_PASSWORD=new-password
railway restart
```

---

## ✅ Checklist Deploy n8n:

- [ ] Railway CLI installed
- [ ] Logged in to Railway
- [ ] n8n project created
- [ ] Environment variables set
- [ ] n8n deployed successfully
- [ ] Public domain generated
- [ ] Can access n8n UI
- [ ] Can login with credentials
- [ ] Test connection to VNStock API
- [ ] Create first workflow
- [ ] Change default password

---

## 🎯 Recommendation:

**Deploy 2 services riêng biệt:**

1. **VNStock API** (Project 1)
   - URL: `https://vnstock-api-production.up.railway.app`
   - Use: `./deploy-now.sh`

2. **n8n** (Project 2)
   - URL: `https://vnstock-n8n-production.up.railway.app`
   - Use: `./deploy-n8n-railway.sh`

**Lý do:**
- ✅ Quản lý độc lập
- ✅ Scale riêng biệt
- ✅ Restart không ảnh hưởng nhau
- ✅ Sử dụng full $5 credit cho mỗi service
- ✅ Dễ debug và monitor

---

## 🚀 Quick Start:

```bash
# 1. Deploy VNStock API
./deploy-now.sh

# 2. Deploy n8n
./deploy-n8n-railway.sh

# 3. Open n8n
railway open

# 4. Create workflow connecting to VNStock API
# Done! 🎉
```

**Tổng thời gian: ~5-7 phút**

---

## 📞 Support:

- n8n Docs: https://docs.n8n.io
- Railway Docs: https://docs.railway.app
- VNStock API: https://github.com/nguyenhoang1221hoangnguyen/vnstock-api

**Happy automating! 🚀**
