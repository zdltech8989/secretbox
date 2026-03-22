# ============ Stage 1: Build frontend ============
FROM node:20-alpine AS frontend

WORKDIR /build

# 安装依赖并构建
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ============ Stage 2: Python dependencies ============
FROM python:3.11-slim AS deps

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    # MySQL 客户端依赖
    apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============ Stage 3: Runtime ============
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制已安装的 Python 依赖
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# 复制应用代码
COPY app/ ./app/
COPY services/ ./services/
COPY bot/ ./bot/
COPY cli/ ./cli/
COPY sql/ ./sql/
COPY --from=frontend /build/dist ./static

# 创建数据目录
RUN mkdir -p /app/data && chown -R 1000:1000 /app/data

# 声明数据卷挂载点 (用于 SQLite 数据库和上传文件)
VOLUME ["/app/data"]

# 使用非 root 用户运行
USER 1000

EXPOSE 9000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
