# Hướng dẫn Setup Docker cho App Server

## Giới thiệu

Đây là hướng dẫn setup **App Server** - server chính của hệ thống AI Teaching Assistant. 

Hệ thống hoàn chỉnh gồm 3 server:
- **App Server** (hướng dẫn này): Frontend, Backend API, Database
- **n8n Server** (riêng): Automation workflows
- **AI Server** (riêng): PhoGPT model và RAG

## Cấu trúc thư mục App Server
```
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py         # Cấu hình app, lấy biến môi trường
│   │   └── __init__.py
│   ├── database/
│   │   ├── session.py        # Kết nối và tạo session DB
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py           # Định nghĩa ORM models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py           # Định nghĩa Pydantic schemas
│   │   └── __init__.py
│   ├── crud/
│   │   ├── user.py           # Xử lý truy vấn DB (CRUD)
│   │   └── __init__.py
│   ├── services/
│   │   ├── user_service.py   # Xử lý logic nghiệp vụ
│   │   └── __init__.py
│   ├── api/
│   │   ├── deps.py           # Các dependency chung
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── user.py   # Định nghĩa router (controller)
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── requirements.txt
├── .env
├── .env.dev
└── .env.prod
```

## Quick Start

### 1. Clone repository
```bash
git clone <repository-url>
cd ai-teaching-assistant
```

### 2. Setup environment
```bash
# Copy file env mẫu
cp .env.example .env

# Edit file .env - CẦN CẬP NHẬT:
# - DISCORD_TOKEN: Token bot Discord của bạn
# - N8N_WEBHOOK_URL: URL webhook của n8n server
# - AI_SERVICE_URL: URL API của AI server
nano .env
```

### 3. Cấp quyền cho script
```bash
chmod +x docker-control.sh
```

### 4. Start App Server
```bash
# Start toàn bộ App Server
./docker-control.sh start

# Hoặc start từng phần:
./docker-control.sh start-backend   # Chỉ backend services
./docker-control.sh start-frontend  # Chỉ frontend
```

### 5. Kiểm tra services
```bash
# Check health status
./docker-control.sh health

# Xem logs
./docker-control.sh logs
```

## Services trong App Server

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Vue.js web interface |
| Backend API | 8000 | FastAPI REST API |
| MySQL | 3306 | Main database |
| Redis | 6379 | Cache & session storage |
| Discord Bot | - | Bot kết nối Discord |
| Adminer | 8080 | Database management UI |

## Truy cập

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Adminer**: http://localhost:8080
  - Server: `mysql`
  - Username: `root`
  - Password: `rootpassword`
  - Database: `ai_assistant`

## Kết nối với External Services

### 1. Kết nối với n8n Server

Trong `.env`, cấu hình:
```bash
N8N_WEBHOOK_URL=http://n8n-server-ip:5678/webhook/your-webhook-id
```

Discord bot và Backend API sẽ gửi requests đến URL này.

### 2. Kết nối với AI Server

Trong `.env`, cấu hình:
```bash
AI_SERVICE_URL=http://ai-server-ip:port/api
AI_API_KEY=your-api-key-if-required
```

Backend sẽ gọi AI server khi cần xử lý chat.

## Các lệnh hữu ích

```bash
# Xem logs của service cụ thể
./docker-control.sh logs backend
./docker-control.sh logs mysql

# Restart all services
./docker-control.sh restart

# Rebuild images (sau khi change code)
./docker-control.sh build

# Initialize database
./docker-control.sh init-db

# Reset toàn bộ data (CẢNH BÁO!)
./docker-control.sh reset
```

## Manual Docker Commands

```bash
# Start với docker-compose trực tiếp
docker-compose -f docker-compose.backend.yml up -d
docker-compose -f docker-compose.frontend.yml up -d

# Vào container shell
docker exec -it ai_assistant_backend bash
docker exec -it ai_assistant_mysql mysql -u root -p

# View container logs
docker logs -f ai_assistant_backend
```

## Troubleshooting

### Port đã được sử dụng
```bash
# Check process đang dùng port
lsof -i :3000
lsof -i :8000

# Kill process hoặc đổi port trong docker-compose
```

### MySQL không start
```bash
# Check logs
docker logs ai_assistant_mysql

# Reset MySQL data
docker volume rm <project>_mysql_data
```

### Discord bot không kết nối
- Kiểm tra DISCORD_TOKEN trong .env
- Check logs: `docker logs ai_assistant_discord_bot`
- Đảm bảo bot đã được invite vào server

### Cannot connect to external services
- Kiểm tra N8N_WEBHOOK_URL và AI_SERVICE_URL
- Test connection: `curl http://n8n-server:5678`
- Check firewall rules giữa servers

## Development Tips

1. **Code changes**: Tự động reload nhờ volume mounts
2. **Database migrations**: Run trong backend container
3. **Test APIs**: Use Swagger UI at /docs
4. **Add packages**:
   ```bash
   # Backend
   docker exec -it ai_assistant_backend pip install <package>
   # Then add to requirements.txt
   
   # Frontend
   docker exec -it ai_assistant_frontend npm install <package>
   ```

## Production Deployment

Khi deploy production:

1. **Update .env**:
   - Change all passwords
   - Set secure SECRET_KEY
   - Update external service URLs

2. **Remove development features**:
   - Remove Adminer service
   - Disable code reload
   - Remove volume mounts for code

3. **Add security**:
   - Setup HTTPS với nginx
   - Configure firewall
   - Limit exposed ports

4. **Create production compose file**:
   ```yaml
   # docker-compose.prod.yml
   # Remove volumes, add restart policies
   ```

## Backup

### Database backup
```bash
# Backup
docker exec ai_assistant_mysql mysqldump -u root -prootpassword ai_assistant > backup.sql

# Restore
docker exec -i ai_assistant_mysql mysql -u root -prootpassword ai_assistant < backup.sql
```

### Files backup
```bash
# Backup uploaded files
tar -czf uploads-backup.tar.gz backend/uploads/
```

## Support

Nếu gặp vấn đề:
1. Check logs với `./docker-control.sh logs`
2. Verify health với `./docker-control.sh health`
3. Check external service connectivity
4. Review .env configuration