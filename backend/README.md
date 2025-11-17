# BTEC AI Teaching Assistant - Backend

Backend API sử dụng **FastAPI** (Python) và MySQL.

## Cấu trúc thư mục

```
backend/
├── app/                    # Thư mục chứa toàn bộ source code
│   ├── main.py            # File chính chứa FastAPI application (DUY NHẤT)
│   ├── core/              # Cấu hình, security, middleware
│   ├── crud/              # Database operations
│   ├── database/          # Database connection và session
│   ├── dependencies/      # FastAPI dependencies
│   ├── models/            # SQLAlchemy models
│   ├── routes/            # API endpoints
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── cache/             # Redis cache client
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Base docker compose
├── docker-compose.dev.yml # Development overrides
├── docker-compose.prod.yml # Production overrides
├── .env.dev              # Development environment variables
├── .env.prod             # Production environment variables
└── run-dev.sh            # Development startup script
```

## Quan trọng: Chỉ có 1 file main.py

- **File main duy nhất**: `backend/app/main.py`
- **Không có file main.py nào khác** ở ngoài thư mục app
- Cấu trúc này đảm bảo:
  - Tránh nhầm lẫn trong deployment
  - Dễ dàng maintain và debug
  - Phù hợp với Docker container structure

## Tự động tạo bảng Database

- **Startup Event**: Ứng dụng tự động tạo bảng database khi khởi động
- **Hoạt động ở mọi môi trường**: Development, Production, Docker
- **Không cần script riêng**: Không cần chạy migration manual
- **Log rõ ràng**: Hiển thị thông báo tạo bảng thành công/thất bại

## Deployment

### Development
```bash
cd backend
./run-dev.sh
```

### Production
```bash
cd backend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Docker Build
```bash
cd backend
docker-compose build
```

## Cấu hình Docker

- **Dockerfile**: Copy code vào `/app/app` và set working directory
- **PYTHONPATH**: Được set thành `/app/app` để import modules đúng cách
- **CMD**: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Environment Variables

Tạo file `.env` từ template tương ứng:
- Development: Copy từ `.env.dev`
- Production: Copy từ `.env.prod`

## API Documentation

Khi server chạy, truy cập:
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/`

## Troubleshooting

### Lỗi import modules
- Kiểm tra PYTHONPATH đã được set đúng `/app/app`
- Đảm bảo working directory trong container là `/app/app`

### Lỗi database connection
- Kiểm tra file `.env` có đúng database credentials
- Đảm bảo database server đã chạy và accessible

### Container không start
- Kiểm tra logs: `docker-compose logs api`
- Rebuild image: `docker-compose build --no-cache`
