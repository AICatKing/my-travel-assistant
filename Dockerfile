# --- 第一阶段: 构建依赖 ---
FROM python:3.11-slim AS builder

# 安装 uv，用于极速同步依赖
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /app

# 1. 拷贝依赖定义文件
COPY pyproject.toml uv.lock ./

# 2. 执行标准同步（彻底移除所有 --mount 缓存挂载，确保 100% 云端兼容性）
# --frozen: 强制根据 uv.lock 进行精确还原
# --no-install-project: 仅安装库，暂不安装当前项目包，以加快缓存命中
RUN uv sync --frozen --no-install-project --no-dev

# --- 第二阶段: 运行时环境 (最小化镜像) ---
FROM python:3.11-slim

WORKDIR /app

# 从 builder 阶段拷贝已准备好的虚拟环境 (.venv)
COPY --from=builder /app/.venv /app/.venv

# 拷贝后端核心源代码
COPY src /app/src

# 设置生产环境必要的变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1

# 暴露 FastAPI 的生产端口
EXPOSE 8000

# 运行命令：使用 uvicorn 直接启动，监听 0.0.0.0 以供容器外访问
CMD ["uvicorn", "api.main.app", "--host", "0.0.0.0", "--port", "8000"]
