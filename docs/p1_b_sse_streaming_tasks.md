# 任务 P1-B：流式输出 (SSE) 执行清单

**目标**: 实现 Agent 思考过程的实时同步，消除用户在生成长计划时的等待焦虑。

---

## 🟢 第一部分：后端流式接口 (Backend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **SSE-B1** | **状态生成器开发** | 在 `main.py` 编写异步生成器，包装 `graph.astream` | `feat(api): add async generator for sse streaming` |
| **SSE-B2** | **路由升级** | 新增 `/api/plan/stream` 接口，返回 `StreamingResponse` | `feat(api): add /api/plan/stream endpoint` |
| **SSE-B3** | **中间状态过滤** | 映射 LangGraph 节点名到用户可读的中文字符串（如 `planner` -> `正在生成行程...`） | `refactor(api): map agent nodes to user-friendly status` |
| **SSE-B4** | **数据格式封装** | 统一 SSE 消息格式：`data: {"type": "status", "content": "..."}` 和 `data: {"type": "final", "content": {...}}` | `feat(api): standardize sse message format` |

---

## 🔵 第二部分：前端流式消费 (Frontend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **SSE-F1** | **Fetch Stream 适配** | 在 `api.ts` 新增 `createStreamPlan` 方法，处理 `ReadableStream` | `feat(web): add fetch streaming client` |
| **SSE-F2** | **状态反馈 UI** | 在 `App.vue` 增加 `currentStatus` 变量，实时显示 Agent 当前所在的节点 | `feat(web): add real-time status display in loading state` |
| **SSE-F3** | **响应式更新** | 确保最终计划接收完毕后，平滑替换 Loading 状态为结果卡片 | `feat(web): integrate streaming response into ui flow` |

---

## 🚦 执行准则 (Guidelines)

### ✅ 任务 (Do)
*   **Keep-Alive**: 确保 SSE 连接在长时间推理（30s+）中不会断开。
*   **JSON 序列化**: 每一条 `data:` 消息都应是合法的 JSON 字符串。
*   **并发安全**: 确保每个用户的流连接是独立的，状态不会混淆。

### ❌ 禁忌 (Do Not)
*   不要向前端发送过于技术化的 Trace 信息（如：LangChain 的具体 Trace ID）。
*   不要在流式传输中使用 `axios`（axios 对流式响应的支持不如原生的 `fetch` 直观）。

### ⚠️ 约束 (Constraints)
*   由于使用 `astream`，后端需要从 `initial_state` 开始手动触发图运行。

### 📈 成功指标 (Success Signals)
*   前端点击按钮后，1秒内出现“正在搜寻景点...”。
*   随后动态变为“正在查询天气...”、“正在生成最终行程...”。
*   最终无缝显示完整旅行计划。
