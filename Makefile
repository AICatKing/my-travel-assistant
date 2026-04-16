# --- 变量定义 ---
PYTHON = python
UV = uv
NPM = npm
FRONTEND_DIR = web
BACKEND_MAIN = src/api/main.py

.PHONY: all help install dev backend frontend clean

help:
	@echo "可用命令:"
	@echo "  make install  - 安装前后端所有依赖"
	@echo "  make dev      - [推荐] 并行启动前端和后端"
	@echo "  make backend  - 仅启动 FastAPI 后端"
	@echo "  make frontend - 仅启动 Vue3 前端"
	@echo "  make clean    - 清理缓存和临时文件"

# --- 依赖安装 ---
install: install-backend install-frontend

install-backend:
	@echo "正在安装后端依赖 (uv)..."
	$(UV) sync

install-frontend:
	@echo "正在安装前端依赖 (npm)..."
	cd $(FRONTEND_DIR) && $(NPM) install

# --- 服务启动 ---

# 使用 -j 2 实现并行运行，CTRL+C 可同时停止
dev:
	@echo "正在启动全栈开发环境..."
	@$(MAKE) -j 2 backend frontend

backend:
	@echo "启动后端 API (localhost:8000)..."
	@PYTHONPATH=src $(PYTHON) $(BACKEND_MAIN)

frontend:
	@echo "启动前端界面 (localhost:5173)..."
	@cd $(FRONTEND_DIR) && $(NPM) run dev

# --- 清理 ---
clean:
	rm -rf .venv
	rm -rf $(FRONTEND_DIR)/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(FRONTEND_DIR)/dist
