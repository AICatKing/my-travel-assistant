# 智能旅行助手 (My Travel Assistant) 开发路线图

本路线图旨在指导从当前的 LangGraph 后端逻辑向全栈 Web 应用的演进。

---

## 🚀 阶段 1 (P0): 核心链路打通 (MVP - 最小可行性产品)
**目标 (Goal)**: 将 Agent 逻辑封装为 Web API，并通过前端表单实现端到端的闭环。

### ✅ 任务 (Do)
1.  **FastAPI 后端集成**:
    *   创建 `src/api/main.py`，实现 `/api/plan` 接口。
    *   配置 CORS 允许前端跨域访问。
2.  **Vue3 基础开发**:
    *   初始化 Vue3 + TypeScript + TailwindCSS 项目。
    *   实现核心输入表单（城市、日期、偏好、预算）。
3.  **Docker 部署准备**:
    *   验证本地 Docker 镜像构建并成功运行容器。
    *   在本地通过 `.env` 文件加载密钥。

### ❌ 禁忌 (Do Not)
*   不要在此阶段开发用户登录/注册系统。
*   不要纠结于 UI 的精美程度，优先保证接口调通。
*   不要在前端处理复杂的地理计算，逻辑应留在后端。

### ⚠️ 约束 (Constraints)
*   必须复用现有的 `src/agent/models.py` 定义，确保前后端数据结构严丝合缝。
*   所有 API 响应超时时间需设置为 60s 以上（Agent 推理较慢）。

### 📈 成功指标 (Success Signals)
*   前端点击“生成计划”后，能接收到后端的 JSON 数据并在页面以文字列表形式展示。
*   后端容器能在 8000 端口正常提供 Swagger 文档 (`/docs`)。

---

## 🎨 阶段 2 (P1): 视觉与交互增强
**目标 (Goal)**: 提升用户的感知体验，引入地图可视化与多媒体内容。

### ✅ 任务 (Do)
1.  **高德地图 JS API 集成**:
    *   在 Vue3 页面中加载地图，并根据后端返回的 `Location` 进行打点。
    *   实现景点间的连线，展示行程路径。
2.  **Unsplash 视觉插件**:
    *   在 `tools.py` 增加 Unsplash 图片搜索工具。
    *   在 `TripPlan` 模型中增加 `image_url` 字段，并在前端展示精美背景图。
3.  **流式输出 (SSE)**:
    *   将 API 改为 `StreamingResponse`，实时反馈 Agent 的思考步骤（如：“正在查询上海天气...”）。

### ❌ 禁忌 (Do Not)
*   不要过度调用 Unsplash/高德 API，避免触发免费额度上限。
*   不要在地图上加载过多的 3D 效果，保证低端机型的流畅度。

### ⚠️ 约束 (Constraints)
*   必须处理 AMap API 加载失败的优雅降级。
*   图片资源需使用 HTTPS 链接以确保线上部署安全。

### 📈 成功指标 (Success Signals)
*   生成的行程卡片带有对应景点的真实照片。
*   地图能随着行程的生成自动缩放（FitView）并展示所有打点。

---

## 🛡️ 阶段 3 (P2): 生产级稳定性与持久化
**目标 (Goal)**: 确保系统在高并发下的稳定性，并支持用户保存历史记录。

### ✅ 任务 (Do)
1.  **Redis 记忆存储**:
    *   集成 Upstash Redis，配置 LangGraph 的 `PostgresSaver` 或自定义 Redis Checkpointer。
    *   实现对话状态持久化，刷新页面后行程不丢失。
2.  **PDF/图片导出**:
    *   前端集成 `html2canvas` 或 `jspdf`，支持用户将计划保存为高清图片或 PDF。
3.  **线上部署部署**:
    *   部署至 Zeabur (后端) + Vercel (前端)。
    *   配置自定义域名与 SSL 证书。

### ❌ 禁忌 (Do Not)
*   不要在公网暴露 Redis/Database 的原始连接字符串。
*   不要在免费实例上运行内存占用超过 512MB 的模型。

### ⚠️ 约束 (Constraints)
*   必须实现 API 限流 (Rate Limiting)，防止单一用户恶意刷量。
*   必须在 CI/CD 流程中加入自动化测试。

### 📈 成功指标 (Success Signals)
*   用户关闭浏览器再次打开后，之前的旅行规划依然显示。
*   系统在 5 人并发生成计划时，CPU 与内存占用保持稳定。
