# --- 第一阶段: 构建依赖 ---
FROM python:3.11-slim AS builder

# 安装 uv (极速 Python 包管理器)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /app

# 1. 缓存依赖项 (利用 Docker 层缓存)
# 只有在 pyproject.toml 或 uv.lock 改变时才会重新安装
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# --- 第二阶段: 运行时环境 ---
FROM python:3.11-slim

WORKDIR /app

# 从 builder 拷贝已安装好的虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 拷贝源代码 (注意：这里直接把 src 拷贝过去)
COPY src /app/src

# 设置核心环境变量
# 1. 将 .venv/bin 加入 PATH (这样可以直接运行 python/uvicorn)
# 2. 将 src 加入 PYTHONPATH (确保 import agent 能找对位置)
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 运行命令 (生产环境推荐使用 uvicorn)
# --host 0.0.0.0 必选，否则外部无法访问容器
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
