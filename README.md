# Hướng dẫn Setup Docker cho App Server

## Giới thiệu

## Cấu trúc thư mục App Server
```
.
├── backend
│   └── app
│       ├── api
│       ├── core
│       ├── crud
│       ├── database
│       ├── models
│       ├── routes
│       ├── schemas
│       ├── services
│       ├── .env.dev
│       ├── .env.prod
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── docker-compose.dev.yml
│       ├── docker-compose.prod.yml
│       ├── docker-compose.yml
│       └── run-dev.sh  // TODO: Script để chạy dev server
│
│
├── discord-bot
│   ├── bot.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── frontend
    ├── public
    ├── Dockerfile
    ├── docker-compose.dev.yml
    └── src
        ├── api
        ├── assets
        ├── components
        ├── pages
        ├── router
        ├── utils
        ├── App.vue
        └── main.js

```

## Quick Start

### 1. Clone repository
### 2. Run backend server
```bash
cd backend/app
chmod +x run-dev.sh
./run-dev.sh
```
