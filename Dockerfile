# --- 第一阶段: 构建依赖 ---
FROM python:3.11-slim AS builder

# 安装 uv，用于极速同步依赖
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /app

# 1. 拷贝依赖定义文件
COPY pyproject.toml uv.lock ./

# 2. 执行标准同步（彻底移除所有 --mount 缓存挂载，确保 100% 云端兼容性）
RUN uv sync --frozen --no-install-project --no-dev

# --- 第二阶段: 运行时环境 (最小化镜像) ---
FROM python:3.11-slim

WORKDIR /app

# 从 builder 阶段拷贝已准备好的虚拟环境 (.venv)
COPY --from=builder /app/.venv /app/.venv

# 拷贝后端核心源代码 (将整个 src 拷贝到 /app/src)
COPY src /app/src

# 设置生产环境必要的变量
# 1. 确保可以直接运行虚拟环境中的二进制文件 (如 uvicorn)
# 2. 确保 Python 能够正确 import /app/src 下的模块
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1

# 暴露 FastAPI 的生产端口
EXPOSE 8000

# 运行命令：使用冒号 : 分隔 api.main 和 app
# 确保没有多余的空格或拼写错误
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
