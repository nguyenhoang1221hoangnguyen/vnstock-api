# VNStock API - Hướng dẫn Docker Chi tiết

## 🐳 Tổng quan

VNStock API được đóng gói sẵn với Docker và docker-compose, bao gồm cả n8n để tạo thành một stack hoàn chỉnh.

## 📦 Kiến trúc Docker Stack

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│       vnstock-network                   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ VNStock API  │  │     n8n      │   │
│  │   :8000      │◄─┤   :5678      │   │
│  └──────────────┘  └──────────────┘   │
│         │                              │
└─────────┼──────────────────────────────┘
          │
    ┌─────▼──────┐
    │   Volumes  │
    ├────────────┤
    │ n8n_data   │
    │ ./logs     │
    └────────────┘
```

## 🚀 Quick Start

### Bước 1: Kiểm tra yêu cầu

```bash
# Kiểm tra Docker
docker --version
# Docker version 24.0.0 trở lên

# Kiểm tra Docker Compose
docker-compose --version
# docker-compose version 1.29.0 trở lên
```

### Bước 2: Khởi động Stack

```bash
cd vnstock-api
./docker-start.sh
```

Script sẽ tự động:
1. Kiểm tra Docker đã cài đặt
2. Tạo file `.env` từ `.env.example` nếu chưa có
3. Tạo các thư mục cần thiết
4. Build Docker images
5. Khởi động containers
6. Hiển thị thông tin truy cập

### Bước 3: Truy cập Services

- **VNStock API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678
  - Username: `admin`
  - Password: `admin123`

## 🔧 Cấu hình Docker

### File docker-compose.yml

```yaml
services:
  vnstock-api:
    build: .
    ports:
      - "8000:8000"
    networks:
      - vnstock-network

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    depends_on:
      - vnstock-api
    networks:
      - vnstock-network
    volumes:
      - n8n_data:/home/node/.n8n
```

### Environment Variables

File `.env`:

```bash
# n8n Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
N8N_HOST=localhost
WEBHOOK_URL=http://localhost:5678/

# Timezone
TIMEZONE=Asia/Ho_Chi_Minh

# VNStock API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
NODE_ENV=production
```

## 📝 Các lệnh Docker

### Khởi động và Dừng

```bash
# Khởi động stack
./docker-start.sh

# Dừng stack
./docker-stop.sh

# Khởi động lại
docker-compose restart

# Khởi động một service cụ thể
docker-compose restart vnstock-api
docker-compose restart n8n
```

### Quản lý Containers

```bash
# Xem trạng thái containers
docker-compose ps

# Xem logs
docker-compose logs -f
docker-compose logs -f vnstock-api
docker-compose logs -f n8n

# Xem logs 100 dòng cuối
docker-compose logs --tail=100 vnstock-api

# Vào container
docker-compose exec vnstock-api /bin/bash
docker-compose exec n8n /bin/sh
```

### Build và Rebuild

```bash
# Build images
docker-compose build

# Rebuild từ đầu (no cache)
./docker-rebuild.sh

# Build một service cụ thể
docker-compose build vnstock-api
```

### Dọn dẹp

```bash
# Dừng và xóa containers
docker-compose down

# Dừng, xóa containers và volumes
docker-compose down -v

# Dừng, xóa containers và images
docker-compose down --rmi all

# Dừng và xóa tất cả (containers, volumes, images)
docker-compose down -v --rmi all

# Xóa images không sử dụng
docker image prune -a
```

## 🔗 Kết nối giữa Services

### Từ n8n đến VNStock API

Trong Docker network, các containers giao tiếp với nhau qua tên service:

```
URL: http://vnstock-api:8000/api/stock/VNM
```

**KHÔNG dùng**: `http://localhost:8000` (sẽ không hoạt động)

### Từ bên ngoài (host machine)

```
URL: http://localhost:8000/api/stock/VNM
```

## 📊 Health Checks

VNStock API có sẵn health check endpoint:

```bash
# Kiểm tra health từ host
curl http://localhost:8000/health

# Kiểm tra health từ bên trong container
docker-compose exec vnstock-api curl http://localhost:8000/health
```

Docker tự động kiểm tra health mỗi 30 giây:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 💾 Volumes và Data Persistence

### n8n Data

Workflows và dữ liệu n8n được lưu trong Docker volume:

```bash
# Xem volumes
docker volume ls | grep n8n

# Inspect volume
docker volume inspect n8n_data

# Backup n8n data
docker run --rm -v n8n_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/n8n-backup.tar.gz /data

# Restore n8n data
docker run --rm -v n8n_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/n8n-backup.tar.gz -C /
```

### Logs

Logs được mount từ host:

```bash
# Xem logs
tail -f logs/app.log

# Xóa logs
rm -rf logs/*.log
```

## 🔐 Security Best Practices

### 1. Thay đổi mật khẩu n8n

Trong file `.env`:

```bash
N8N_BASIC_AUTH_USER=your_username
N8N_BASIC_AUTH_PASSWORD=strong_password_here
```

Sau đó restart:

```bash
docker-compose restart n8n
```

### 2. Giới hạn CORS (Production)

Sửa file `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-domain.com"],  # Thay vì ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Sử dụng HTTPS

Thêm reverse proxy (nginx/traefik) với SSL certificate.

## 🐛 Troubleshooting

### Container không khởi động

```bash
# Xem logs chi tiết
docker-compose logs vnstock-api

# Kiểm tra port đã bị chiếm
lsof -i :8000
lsof -i :5678

# Rebuild từ đầu
./docker-rebuild.sh
```

### n8n không kết nối được VNStock API

1. Kiểm tra cả hai containers cùng network:
```bash
docker network inspect vnstock-network
```

2. Kiểm tra DNS resolution:
```bash
docker-compose exec n8n ping vnstock-api
```

3. Đảm bảo sử dụng `http://vnstock-api:8000` KHÔNG phải `localhost`

### Out of memory

Tăng memory limit trong `docker-compose.yml`:

```yaml
services:
  vnstock-api:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Permission issues

```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) .

# Fix permissions
chmod -R 755 .
```

## 🚀 Production Deployment

### Sử dụng Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml vnstock

# Xem services
docker stack services vnstock

# Xem logs
docker service logs vnstock_vnstock-api
```

### Sử dụng External Database cho n8n

Thêm PostgreSQL vào `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

  n8n:
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n

volumes:
  postgres_data:
```

## 📈 Monitoring

### Resource Usage

```bash
# CPU/Memory usage
docker stats

# Disk usage
docker system df
```

### Container Logs

```bash
# Follow logs
docker-compose logs -f --tail=100

# Export logs
docker-compose logs > vnstock-logs.txt
```

## 🔄 Updates

### Update VNStock API

```bash
# Pull latest changes
git pull

# Rebuild và restart
./docker-rebuild.sh
```

### Update n8n

```bash
# Pull latest image
docker-compose pull n8n

# Restart với image mới
docker-compose up -d n8n
```

## 📚 Tài liệu tham khảo

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [n8n Documentation](https://docs.n8n.io/)
- [VNStock Documentation](https://github.com/thinh-vu/vnstock)
