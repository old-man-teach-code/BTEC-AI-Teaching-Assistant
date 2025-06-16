# BTEC AI Teaching Assistant – Frontend

Frontend sử dụng **Vue 3**, cấu trúc module hóa hiện đại, dễ mở rộng và bảo trì.  
Dưới đây là hướng dẫn triển khai code dựa trên base template hiện tại, tham khảo phong cách tổ chức như backend.

---

## Cấu trúc thư mục chính

```
frontend/
├── public/                  # Static files (favicon, robots.txt, manifest, ...)
├── src/
│   ├── api/                 # Gọi API backend, khai báo các endpoint, axios instance
│   ├── assets/              # Ảnh, font, css dùng chung
│   ├── components/          # Vue components dùng lại nhiều nơi (Button, Modal, ...)
│   ├── router/              # Định nghĩa router (index.js, guards, ...)
│   ├── stores/              # Pinia stores, quản lý state toàn cục
│   ├── utils/               # Hàm tiện ích, helper dùng lại nhiều nơi
│   ├── views/               # Các page chính (Home.vue, Login.vue, Dashboard.vue, ...)
│   ├── App.vue              # Root Vue component
│   └── main.js              # Entry point – khởi tạo app, mount router, store, ...
├── .env.dev                 # Biến môi trường cho dev
├── .env.example             # Mẫu file env
├── .env.prod                # Biến môi trường cho production
├── Dockerfile               # Đóng gói FE thành image
├── docker-compose.yml       # Docker Compose phục vụ build/chạy FE (thường dùng kèm backend)
├── nginx.conf               # NGINX cấu hình khi deploy production
├── package.json             # Khai báo dependency & script npm
├── package-lock.json
├── vite.config.js           # Cấu hình Vite
├── run-dev.sh               # Script tiện chạy môi trường dev
├── run-prod.sh              # Script chạy production
├── index.html               # HTML template gốc
├── .editorconfig, .gitignore, .gitattributes, .prettierrc.json, eslint.config.js, jsconfig.json
└── README.md
```

---

## Hướng dẫn phát triển code

### 1. Thêm/chỉnh sửa tính năng mới

- **src/views/**  
  Tạo/chỉnh sửa các page chính (mỗi chức năng lớn là 1 view, ví dụ: `Login.vue`, `UserProfile.vue`, `Dashboard.vue`, ...).

- **src/components/**  
  Tạo các component nhỏ, tái sử dụng cho nhiều page (ví dụ: `BaseButton.vue`, `UserCard.vue`, ...).

- **src/api/**  
  Tạo file kết nối/logic với backend (chia nhỏ theo domain: `user.js`, `auth.js`, ...).  
  Đặt axios instance, interceptor tại đây nếu có.

- **src/stores/**  
  Tạo/chỉnh sửa Pinia store cho các state/phần logic chia sẻ giữa các component/page.

- **src/router/**  
  Định nghĩa các route, middlewares/router-guards (bảo vệ route, check quyền, ...).

- **src/utils/**  
  Viết các hàm tiện ích dùng lại nhiều nơi (format date, validate, ...).

- **src/assets/**  
  Để ảnh, icon, font, style css/scss dùng toàn app.

- **App.vue, main.js**  
  Chỉ cấu hình root, setup plugin, mount router/store, không viết logic nghiệp vụ ở đây.

---

## Quy trình triển khai code mới

1. **Tạo view mới** trong `src/views/` nếu là một page mới (ví dụ: `CourseList.vue`)
2. **Tạo component** trong `src/components/` nếu cần tái sử dụng (ví dụ: `CourseCard.vue`)
3. **Khai báo API** trong `src/api/` nếu cần gọi backend (ví dụ: `course.js`)
4. **Quản lý state** với Pinia store trong `src/stores/` nếu logic phức tạp
5. **Thêm route** trong `src/router/` để điều hướng tới view mới
6. **Thêm style, assets** vào `src/assets/` nếu cần

---

## Lưu ý

- **Tách biệt rõ view, component, store, api, utils** để dễ bảo trì.
- **Không để logic xử lý nghiệp vụ vào main.js hay App.vue**.
- **Mỗi domain (user, course, auth, ...) nên tách file api, store, view, component riêng nếu phức tạp**.
- **Sử dụng biến môi trường qua file `.env.*`** (ví dụ: cấu hình endpoint backend, token, ...).

---
