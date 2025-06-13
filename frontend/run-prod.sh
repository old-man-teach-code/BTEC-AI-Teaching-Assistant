#!/bin/bash
echo "Build và chạy frontend PRODUCTION mode..."
docker compose -f docker-compose.yml up --build frontend-prod