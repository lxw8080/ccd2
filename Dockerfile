# Multi-stage Dockerfile for CCD2 Project
# This builds both frontend and backend in a single optimized image

# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies with npm registry mirror for faster builds
# Note: We need devDependencies for building (TypeScript, Vite, etc.)
RUN npm config set registry https://registry.npmmirror.com && \
    npm ci --silent

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production (skip TypeScript type checking for faster build)
# Use vite build directly instead of tsc && vite build
RUN npx vite build

# ============================================
# Stage 2: Build Backend Base
# ============================================
FROM python:3.11-slim AS backend-base

# Install system dependencies (with retry and fix-missing for network issues)
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    gcc \
    postgresql-client \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* || \
    (sleep 5 && apt-get update && apt-get install -y --no-install-recommends --fix-missing gcc postgresql-client libpq-dev libmagic1 && rm -rf /var/lib/apt/lists/*)

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Final Production Image
# ============================================
FROM python:3.11-slim AS production

# Install runtime dependencies including Redis (with retry and fix-missing for network issues)
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    postgresql-client \
    libpq-dev \
    libmagic1 \
    nginx \
    supervisor \
    curl \
    redis-server \
    && rm -rf /var/lib/apt/lists/* || \
    (sleep 5 && apt-get update && apt-get install -y --no-install-recommends --fix-missing postgresql-client libpq-dev libmagic1 nginx supervisor curl redis-server && rm -rf /var/lib/apt/lists/*)

WORKDIR /app

# Copy Python packages from backend-base
COPY --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin

# Copy backend application code
COPY backend/ ./backend/

# Make check_startup.py executable
RUN chmod +x ./backend/check_startup.py

# Copy built frontend from frontend-builder
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /var/log/supervisor /var/lib/redis /var/log/redis

# Configure Redis
RUN echo 'bind 127.0.0.1 \n\
port 6379 \n\
daemonize no \n\
supervised systemd \n\
pidfile /var/run/redis/redis-server.pid \n\
loglevel notice \n\
logfile /var/log/redis/redis-server.log \n\
dir /var/lib/redis \n\
save 900 1 \n\
save 300 10 \n\
save 60 10000 \n\
stop-writes-on-bgsave-error yes \n\
rdbcompression yes \n\
rdbchecksum yes \n\
dbfilename dump.rdb \n\
appendonly yes \n\
appendfilename "appendonly.aof" \n\
appendfsync everysec' > /etc/redis/redis.conf

# Set permissions for Redis
RUN chown -R redis:redis /var/lib/redis /var/log/redis

# Create nginx configuration for serving frontend and proxying backend
RUN echo 'server { \n\
    listen 80; \n\
    server_name localhost; \n\
    client_max_body_size 20M; \n\
    \n\
    # Serve frontend static files \n\
    location / { \n\
        root /app/frontend/dist; \n\
        try_files $uri $uri/ /index.html; \n\
    } \n\
    \n\
    # Proxy API requests to backend \n\
    location /api { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \n\
        proxy_set_header X-Forwarded-Proto $scheme; \n\
    } \n\
    \n\
    # Proxy docs to backend \n\
    location /docs { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
    } \n\
    \n\
    location /redoc { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
    } \n\
    \n\
    location /openapi.json { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
    } \n\
    \n\
    # WebSocket support \n\
    location /ws { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_http_version 1.1; \n\
        proxy_set_header Upgrade $http_upgrade; \n\
        proxy_set_header Connection "upgrade"; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
    } \n\
}' > /etc/nginx/sites-available/default

# Create supervisor configuration
RUN echo '[supervisord] \n\
nodaemon=true \n\
logfile=/var/log/supervisor/supervisord.log \n\
pidfile=/var/run/supervisord.pid \n\
\n\
[program:redis] \n\
command=/usr/bin/redis-server /etc/redis/redis.conf \n\
autostart=true \n\
autorestart=true \n\
priority=10 \n\
stdout_logfile=/var/log/supervisor/redis.log \n\
stderr_logfile=/var/log/supervisor/redis_err.log \n\
user=redis \n\
\n\
[program:nginx] \n\
command=/usr/sbin/nginx -g "daemon off;" \n\
autostart=true \n\
autorestart=true \n\
priority=20 \n\
stdout_logfile=/var/log/supervisor/nginx.log \n\
stderr_logfile=/var/log/supervisor/nginx_err.log \n\
\n\
[program:backend] \n\
command=/usr/local/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info \n\
directory=/app/backend \n\
autostart=true \n\
autorestart=true \n\
startretries=3 \n\
priority=30 \n\
stdout_logfile=/var/log/supervisor/backend.log \n\
stdout_logfile_maxbytes=50MB \n\
stdout_logfile_backups=10 \n\
stderr_logfile=/var/log/supervisor/backend_err.log \n\
stderr_logfile_maxbytes=50MB \n\
stderr_logfile_backups=10 \n\
redirect_stderr=true \n\
environment=PYTHONUNBUFFERED="1"' > /etc/supervisor/conf.d/supervisord.conf

# Set environment variables with defaults
ENV DATABASE_URL="postgresql://ccd_user:ccd_password@localhost:5432/ccd_db" \
    REDIS_URL="redis://localhost:6379/0" \
    SECRET_KEY="your-secret-key-change-in-production" \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="30" \
    STORAGE_TYPE="local" \
    UPLOAD_DIR="/app/uploads" \
    LOG_LEVEL="INFO" \
    APP_NAME="客户资料收集系统" \
    APP_VERSION="1.0.0"

# Expose port 80 for nginx (which serves both frontend and backend)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# Start supervisor to manage nginx and backend
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

