# 🐙 GitHub Setup Instructions

## Bước 1: Tạo Repository trên GitHub

### Cách 1: Dùng Web Browser

1. **Mở trình duyệt** và truy cập: https://github.com/new

2. **Điền thông tin repo:**
   - Repository name: `vnstock-api`
   - Description: `VNStock API v3.3.0 - Vietnamese Stock Market Data API with FastAPI`
   - Visibility:
     - ✅ **Private** (khuyến nghị cho dự án team)
     - hoặc **Public** (nếu muốn share với cộng đồng)

3. **QUAN TRỌNG - KHÔNG chọn:**
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license

   (Vì project đã có sẵn những file này)

4. Click **"Create repository"**

5. **Copy HTTPS URL** hiển thị, ví dụ:
   ```
   https://github.com/YOUR_USERNAME/vnstock-api.git
   ```

---

## Bước 2: Link Local Repository với GitHub

Sau khi tạo repo, GitHub sẽ hiển thị hướng dẫn. Chạy các lệnh sau:

```bash
# Di chuyển vào thư mục project
cd /Users/nguyenhoang/vnstock-api

# Add remote origin (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/vnstock-api.git

# Verify
git remote -v

# Push code lên GitHub
git push -u origin main
```

**Nếu GitHub yêu cầu đăng nhập:**
- Username: GitHub username của bạn
- Password: **KHÔNG PHẢI** password thông thường
  - Phải dùng **Personal Access Token** (PAT)
  - Tạo tại: https://github.com/settings/tokens
  - Chọn: Generate new token (classic)
  - Scopes cần: `repo`, `workflow`

---

## Bước 3: Verify

Sau khi push thành công:

```bash
# Check git status
git status

# Check remote
git remote -v

# Check commits
git log --oneline
```

Truy cập: `https://github.com/YOUR_USERNAME/vnstock-api` để xem code!

---

## Cách 2: Dùng GitHub CLI (Nhanh hơn)

### Cài đặt GitHub CLI

```bash
# macOS
brew install gh

# Verify
gh --version
```

### Tạo repo và push

```bash
# Login
gh auth login

# Tạo repo và push 1 lệnh
gh repo create vnstock-api --private --source=. --remote=origin --push

# Hoặc public repo
gh repo create vnstock-api --public --source=. --remote=origin --push
```

✅ **Xong!** Repo đã được tạo và code đã được push!

---

## Troubleshooting

### Lỗi: Authentication failed

**Giải pháp:**
1. Tạo Personal Access Token:
   - Vào: https://github.com/settings/tokens
   - Click: "Generate new token (classic)"
   - Note: "vnstock-api"
   - Expiration: 90 days (hoặc No expiration)
   - Scopes: Chọn `repo`
   - Click "Generate token"
   - **COPY TOKEN NGAY** (chỉ hiển thị 1 lần)

2. Dùng token thay cho password:
   ```bash
   # Khi git push, nhập:
   # Username: your-github-username
   # Password: paste-your-token-here
   ```

### Lỗi: Remote already exists

```bash
# Remove remote cũ
git remote remove origin

# Add lại
git remote add origin https://github.com/YOUR_USERNAME/vnstock-api.git
```

### Lỗi: Updates were rejected

```bash
# Force push (chỉ dùng cho lần đầu)
git push -u origin main --force
```

---

## Next Step: Deploy to Railway

Sau khi push lên GitHub thành công, chạy:

```bash
./deploy-railway.sh
```

Hoặc deploy từ Railway Dashboard:
1. Vào: https://railway.app
2. New Project → Deploy from GitHub repo
3. Chọn repo `vnstock-api`
4. Done! 🚀
