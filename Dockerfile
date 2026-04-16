# --- 第一阶段: 构建前端 ---
FROM node:22-slim AS frontend-builder

WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# --- 第二阶段: 构建 Python 依赖 ---
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# --- 第三阶段: 运行时环境 ---
FROM python:3.11-slim

# 安装 curl 用于 Railway 健康检查
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src /app/src
COPY --from=frontend-builder /app/web/dist /app/web/dist

# 核心环境变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

# 暴露端口 (虽然 Railway 会覆盖它，但保留声明是好习惯)
EXPOSE 8000

# 运行命令：使用 shell 模式以支持 $PORT 变量解析
WORKDIR /app/src
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
