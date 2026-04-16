# P0 阶段：颗粒度拆解与开发清单 (Sprint 1)

**核心目标**: 实现“用户输入 -> 后端推理 -> 前端展示”的最小闭环。

---

## 🟢 第一部分：后端 FastAPI 开发 (Backend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **B1** | **依赖环境准备** | 安装 `fastapi`, `uvicorn` 并更新 `uv.lock` | `feat(api): add fastapi and uvicorn dependencies` |
| **B2** | **API 骨架搭建** | 创建 `src/api/main.py`，包含根路径健康检查及 CORS 配置 | `feat(api): init fastapi scaffold with cors` |
| **B3** | **集成 Agent 逻辑** | 导入 `graph`，实现 `/api/plan` POST 接口，接收参数并运行 | `feat(api): integrate langgraph agent into /api/plan` |
| **B4** | **错误处理增强** | 增加对高德 Key 缺失、LLM 超时的异常捕获与友好返回 | `fix(api): add exception handling for external services` |
| **B5** | **本地运行脚本** | 在 `Makefile` 或 `package.json` 中添加一键启动后端的命令 | `chore: add server run scripts` |

---

## 🔵 第二部分：前端 Vue3 开发 (Frontend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **F1** | **项目脚手架** | 在根目录创建 `web/` 文件夹，初始化 Vue3 + TS + Vite | `feat(web): init vue3 ts project scaffold` |
| **F2** | **样式基础** | 配置 TailwindCSS 确保基础布局容器就绪 | `feat(web): setup tailwindcss` |
| **F3** | **API 通讯层** | 封装 Axios 或 Fetch，定义与后端一致的 TypeScript 类型 | `feat(web): create api client and types` |
| **F4** | **核心输入表单** | 实现城市、日期、偏好、预算的响应式表单 | `feat(web): add travel request form` |
| **F5** | **结果展示面板** | 实现一个简单的 Loading 状态及结果 JSON/卡片展示 | `feat(web): add basic result display and loading` |

---

## ⚪ 第三部分：基础设施与验证 (Infrastructure)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **D1** | **Dockerfile 验证** | 确保 Docker 镜像能正确启动 FastAPI 服务，并能访问 `src/agent` | `ci: verify backend dockerfile with api module` |
| **D2** | **环境变量链路** | 确保 `.env` 中的 Key 在容器内能正确读取，无硬编码 | `chore: setup production environment variable flow` |
| **D3** | **集成测试** | 编写一个简单的 python 脚本模拟前端调用 `/api/plan` 成功 | `test: add end-to-end api integration test` |

---

## 🚦 开发约束与原则 (Constraints)

1.  **原子化提交**: 每个任务 ID 完成后立即进行 Git Commit，不允许跨 ID 提交。
2.  **不引入冗余**: 阶段 1 严禁加入：用户注册、历史记录数据库、地图可视化（放到 P1）。
3.  **类型同步**: 如果 `agent/models.py` 字段变了，必须同步更新 `web/` 下的 TS 定义。
4.  **失败回滚**: 如果任务 B3 导致 Graph 逻辑崩溃，必须立刻 revert 回 B2 状态并分析原因。
