# BTEC AI Teaching Assistant

> **Monorepo for Backend (FastAPI) & Frontend (Vue3+Vite) development using Docker Compose**

---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt & Chạy phát triển (development)](#cài-đặt--chạy-phát-triển-development)
- [Build & Chạy production](#build--chạy-production)
- [Cấu hình biến môi trường](#cấu-hình-biến-môi-trường)
- [Một số lệnh hữu ích](#một-số-lệnh-hữu-ích)
- [Liên hệ & đóng góp](#liên-hệ--đóng-góp)

---

## Giới thiệu

Repo này chứa toàn bộ mã nguồn frontend (Vue3, Vite) và backend (FastAPI, Python) cho dự án BTEC AI Teaching Assistant.  
Tất cả workflow phát triển và production đều được docker hóa, hỗ trợ khởi động chỉ bằng một lệnh script.

---

## Cấu trúc thư mục

Giả sử cấu trúc repo của bạn như sau (bạn có thể giữ nguyên!):

```
.
├── backend/                   # Chứa toàn bộ mã nguồn backend (FastAPI, Python)
│   ├── app/                   # Code backend (route, model, ...), có thể đổi tùy dự án
│   ├── requirements.txt       # Danh sách thư viện Python
│   ├── Dockerfile             # Dockerfile cho backend
│   ├── docker-compose.yml     # Docker compose riêng cho backend (nếu có)
│   ├── .env.dev               # Biến môi trường mẫu cho dev (backend)
│   ├── .env.prod              # Biến môi trường mẫu cho prod (backend)
│   ├── .env                   # Biến môi trường thực tế (KHÔNG commit lên git)
│   └── run-dev.sh             # Script chạy dev nhanh cho backend
│
├── frontend/                  # Chứa toàn bộ mã nguồn frontend (Vue3, Vite)
│   ├── src/                   # Code Vue (component, store, router, ...)
│   ├── public/                # Static asset cho frontend
│   ├── package.json           # Quản lý package JS
│   ├── Dockerfile             # Dockerfile cho frontend
│   ├── docker-compose.yml     # Docker compose riêng cho frontend (nếu có)
│   ├── .env.dev               # Biến môi trường mẫu cho dev (frontend)
│   ├── .env.prod              # Biến môi trường mẫu cho prod (frontend)
│   ├── .env                   # Biến môi trường thực tế (KHÔNG commit lên git)
│   ├── run-dev.sh             # Script chạy dev nhanh cho frontend
│   └── run-prod.sh            # Script build và chạy frontend production (nếu có)
│
├── README.md                  # Hướng dẫn tổng dự án
└── ...                        # Các file/thư mục khác (docs, .github, scripts, v.v.)
```

**Giải thích sơ:**
- `backend/`: Toàn bộ mã nguồn backend, cấu hình, script, env backend.
- `frontend/`: Toàn bộ mã nguồn frontend, cấu hình, script, env frontend.
- `.env.dev`, `.env.prod`: File cấu hình mẫu, KHÔNG dùng trực tiếp, commit lên repo để mọi người tham khảo.
- `.env`: File thực tế để chạy, auto sinh từ script, KHÔNG commit lên git.
- `run-dev.sh`, `run-prod.sh`: Script giúp khởi động môi trường dev/prod nhanh chóng, tự động setup env.

---

## Yêu cầu hệ thống

- **Docker** >= 20.10.x
- **Docker Compose** >= 2.x
- **(Linux/macOS/Windows đều hỗ trợ)**

---

## Cài đặt & Chạy phát triển (development)

**1. Clone repo:**
```bash
git clone https://github.com/old-man-teach-code/BTEC-AI-Teaching-Assistant.git
cd BTEC-AI-Teaching-Assistant
```

**2. Backend:**
```bash
cd backend

# Tuỳ chọn: Nếu muốn cấu hình biến môi trường cụ thể, chỉnh sửa file .env.dev theo ý bạn
# Nếu không, có thể bỏ qua bước này, script sẽ tự động copy .env.dev thành .env khi chạy

./run-dev.sh
```
- Script sẽ tự động copy `.env.dev` thành `.env`, build & chạy backend cùng database MySQL, auto migrate DB, show log realtime.

**3. Frontend:**
```bash
cd ../frontend

# Tuỳ chọn: Nếu muốn cấu hình biến môi trường cụ thể, chỉnh sửa file .env.dev theo ý bạn
# Nếu không, có thể bỏ qua bước này, script sẽ tự động copy .env.dev thành .env khi chạy

./run-dev.sh
```
- Script sẽ tự động copy `.env.dev` thành `.env`, build & chạy frontend dev server (hot reload), show log realtime.

**4. Truy cập:**
- Backend API: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:5173](http://localhost:5173)

---

## Build & Chạy production

**1. Backend:**
```bash
cd backend

# Tuỳ chọn: Nếu muốn cấu hình biến môi trường production cụ thể, chỉnh sửa file .env.prod trước
# Nếu không, script sẽ tự động copy .env.prod thành .env khi chạy

docker compose up -d --build
```

**2. Frontend:**
```bash
cd ../frontend

# Tuỳ chọn: Nếu muốn cấu hình biến môi trường production cụ thể, chỉnh sửa file .env.prod trước
# Nếu không, script sẽ tự động copy .env.prod thành .env khi chạy

docker compose up -d --build frontend-prod
```
- Frontend production sẽ chạy qua Nginx tại [http://localhost:3000](http://localhost:3000)

---

## Cấu hình biến môi trường

- **.env.dev**  : Mẫu biến môi trường cho dev, commit lên repo.
- **.env.prod** : Mẫu biến môi trường cho production, commit lên repo.
- **.env**    : File thực tế dùng để chạy, luôn được generate tự động từ script, KHÔNG commit lên git (`.gitignore` đã có).

> **Lưu ý:**  
> Bạn có thể tuỳ chỉnh nội dung file `.env.dev` hoặc `.env.prod` trước khi chạy các script để thay đổi cấu hình theo ý muốn.  
> Nếu không cần thay đổi gì, chỉ cần chạy script `./run-dev.sh` hoặc `./run-prod.sh` là đủ, hệ thống sẽ tự động sử dụng cấu hình mặc định.

---

## Một số lệnh hữu ích

- **Dừng toàn bộ containers:**
  ```bash
  docker compose down
  ```
- **Xóa volumes database (reset data):**
  ```bash
  docker volume ls          # tìm volume có tên btecai_mysql_db hoặc db_data
  docker volume rm <volume_name>
  ```
- **Xem log realtime:**
  ```bash
  docker compose logs -f
  ```

---

## Liên hệ & đóng góp

- Mọi thắc mắc, báo lỗi hoặc đóng góp vui lòng mở [Issue](https://github.com/old-man-teach-code/BTEC-AI-Teaching-Assistant/issues) hoặc liên hệ trực tiếp.
- Đóng góp code vui lòng tạo pull request và tuân thủ guideline của dự án.

---

Happy Coding! 🚀
