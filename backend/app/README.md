# BTEC AI Teaching Assistant – Backend

Backend sử dụng **FastAPI** (Python) và MySQL. 
Dưới đây là hướng dẫn triển khai code dựa trên source code base template hiện tại.

---

## Cấu trúc thư mục chính

```
backend/
├── app/
│   ├── main.py
│   ├── core/
│   ├── crud/
│   ├── database/
│   ├── dependencies/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── request.log
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.dev
├── .env.prod
└── run-dev.sh
```

---

## Hướng dẫn phát triển code

### 1. Thêm hoặc chỉnh sửa nghiệp vụ mới

- **models/**  
  Tạo/chỉnh sửa các file model ORM (SQLAlchemy) cho bảng dữ liệu mới.  
  VD: `models/user.py`, `models/course.py`

- **schemas/**  
  Định nghĩa các Pydantic schema cho input/output của API.  
  VD: `schemas/user.py`, `schemas/course.py`

- **crud/**  
  Viết các hàm thao tác dữ liệu: create, read, update, delete...  
  VD: `crud/user.py`, `crud/course.py`

- **services/**  
  Viết các hàm xử lý nghiệp vụ phức tạp, gọi CRUD hoặc tích hợp nhiều nghiệp vụ.  
  VD: `services/user_service.py`, `services/auth_service.py`

- **dependencies/**  
  Đặt các hàm dependency dùng trong routes (vd: lấy user hiện tại, kiểm tra quyền, lấy DB session...).  
  VD: `dependencies/deps.py` hoặc chia nhỏ theo domain.

- **routes/**  
  Định nghĩa API endpoints, import router vào đây.  
  VD: `routes/user.py`, `routes/auth.py`.  
  Mỗi file route nên chỉ xử lý HTTP request, gọi sang service hoặc crud.

- **core/**  
  Đặt các file cấu hình, bảo mật, middleware (vd: config.py, security.py, jwt_middleware.py...)

- **database/**  
  Tạo/kết nối session, khai báo Base cho SQLAlchemy (`database/session.py`).

- **main.py**  
  Chỉ dùng để mount router, middleware, cấu hình CORS, JWT, docs v.v. Không để business logic ở đây.

---

## Quy trình triển khai code mới

1. **Định nghĩa model** (SQLAlchemy) trong `models/`
2. **Tạo schema** (Pydantic) trong `schemas/`
3. **Viết hàm CRUD** trong `crud/`
4. **(Tuỳ chọn) Viết service** trong `services/` nếu logic phức tạp
5. **Thêm dependency** nếu cần trong `dependencies/`
6. **Tạo router** trong `routes/` cho API endpoint
7. **Import router vào `main.py`** để public endpoint

---

## Ví dụ thêm module mới: "Course"

- `models/course.py`  → Định nghĩa bảng `Course`
- `schemas/course.py` → Định nghĩa schema `CourseCreate`, `CourseRead`
- `crud/course.py`   → Hàm tạo/xem/sửa/xoá Course
- `services/course_service.py` (nếu cần nghiệp vụ riêng)
- `routes/course.py`  → Định nghĩa các endpoint `/courses`
- Import router course vào `main.py`  
  ```python
  from routes.course import router as course_router
  app.include_router(course_router, prefix="/courses", tags=["courses"])
  ```

---

## Lưu ý

- Mỗi module (user, auth, course, ...) nên tách các file model, schema, crud, service, route riêng cho dễ bảo trì.
- Không viết business logic lẫn trong router; luôn gọi service hoặc crud.
- Không để logic vào `main.py`.

---

## Tổ chức API: Phân biệt route có middleware và không có middleware

### A. API không sử dụng middleware (public endpoint)
- Import router vào `main.py` và include như thông thường:
  ```python
  from routes.auth import router as auth_router
  app.include_router(auth_router, prefix="/auth", tags=["auth"])
  ```
  → Các endpoint `/auth/*` là public, không qua bất kỳ middleware đặc biệt nào.

### B. API có middleware (bảo vệ bằng JWT, custom middleware, ...)
Có 3 cách triển khai phổ biến:

**1. Dùng sub-app và mount middleware cho nhóm route**
```python
from fastapi import FastAPI
from core.jwt_middleware import JWTAuthMiddleware
from routes.user import router as user_router

protected_app = FastAPI()
protected_app.add_middleware(JWTAuthMiddleware)
protected_app.include_router(user_router, prefix="/users", tags=["users"])

app.mount("/api", protected_app)
```
→ Các route `/api/users/*` sẽ bị middleware kiểm tra (ví dụ JWT). Các route ngoài `/api` (như `/auth`) vẫn public.

**2. Dùng dependencies với router hoặc endpoint**
```python
from fastapi import APIRouter, Depends
from dependencies.deps import get_current_user

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)
# hoặc áp dụng cho từng endpoint
@router.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return current_user
```
→ Áp dụng kiểm tra xác thực cho tất cả hoặc từng endpoint trong router.

**3. Dùng middleware toàn cục**
```python
from core.jwt_middleware import JWTAuthMiddleware
app.add_middleware(JWTAuthMiddleware)
```
→ Mọi request đều phải qua middleware này (cần cẩn trọng nếu có cả route public và private).

### Tổng kết
- Route public: chỉ cần include router vào app chính.
- Route cần bảo vệ: dùng sub-app + middleware hoặc dependencies (ưu tiên dùng dependencies cho xác thực/ủy quyền, sub-app khi cần bảo vệ cả cụm endpoint).
- Không dùng middleware toàn cục nếu có cả public/private API.

---