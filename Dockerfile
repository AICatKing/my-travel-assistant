# --- 第一阶段: 构建依赖 ---
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# --- 第二阶段: 运行时环境 ---
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

# 核心环境变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

EXPOSE 8000

# 运行命令：直接从 src 目录下启动，简化导入路径
WORKDIR /app/src
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
