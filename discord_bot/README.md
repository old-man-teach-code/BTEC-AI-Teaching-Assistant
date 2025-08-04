# Discord Bot

## Cài đặt & chạy local (phát triển)

```bash
cd discord_bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # hoặc tự tạo file .env
# Điền DISCORD_TOKEN vào .env
./run-dev.sh
```

## Chạy bằng Docker Compose (khuyên dùng)

```bash
cd discord_bot
docker-compose up --build
```

## Cấu trúc thư mục

- `bot.py`: Điểm vào của bot, chỉ khởi tạo và load các cogs.
- `cogs/`: Các module chức năng (quản trị, fun, tiện ích...).
- `utils/`: Hàm tiện ích dùng lại nhiều nơi (nếu có).
- `.env`: Token bot, các biến môi trường.
- `run-dev.sh`: Script chạy nhanh local, tự load .env.
- `Dockerfile`, `docker-compose.yml`: Để build/run bot bằng Docker/Docker Compose.

## Mở rộng chức năng

- Thêm file vào `cogs/`, tạo class kế thừa `commands.Cog`, viết lệnh mới.
- Thêm tên cog vào list `initial_extensions` trong `bot.py`.
- Sửa đổi code xong chỉ cần chạy lại bot hoặc nếu dùng Docker Compose sửa là reload (nếu cần hot-reload có thể dùng watchgod, reload...)

## Lưu ý

- Đảm bảo token bí mật, không push file `.env` lên git public.
- Docker sẽ mount code từ host sang container, tiện sửa code.
