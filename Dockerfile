# --- 第一阶段: 构建依赖 ---
FROM python:3.11-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 1. 先拷贝依赖配置文件 (利用 Docker 标准分层缓存)
COPY pyproject.toml uv.lock ./

# 2. 安装依赖 (不再使用 --mount，改用标准安装)
# --frozen 确保版本锁定
RUN uv sync --frozen --no-install-project --no-dev

# --- 第二阶段: 运行时环境 ---
FROM python:3.11-slim

WORKDIR /app

# 从 builder 拷贝已安装好的虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 拷贝源代码
COPY src /app/src

# 设置核心环境变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 运行命令
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
