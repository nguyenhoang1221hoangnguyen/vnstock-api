# Sử dụng Python 3.11 slim image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt dependencies hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Tạo user non-root và các thư mục cần thiết
RUN useradd -m -u 1000 vnstock && \
    mkdir -p /app/.vnstock /app/.ipython && \
    chown -R vnstock:vnstock /app

# Chuyển sang user non-root
USER vnstock

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Command để chạy ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
