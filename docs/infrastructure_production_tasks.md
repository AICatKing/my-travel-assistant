# 第三阶段：基础设施与生产级部署执行清单

**目标**: 将项目从“本地运行”升级为“容器化集群”，确保具备持久化能力、生产级性能和一键部署能力。

---

## 🏗️ 第一部分：生产级容器化 (Dockerization)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **D-B1** | **后端生产级运行** | 使用 `gunicorn` + `uvicorn` 替代开发版 `uvicorn`，增加 Worker 数量 | `chore(api): use gunicorn for production serving` |
| **D-F1** | **前端容器化** | 编写 `web/Dockerfile`（多阶段构建），使用 Nginx 托管静态文件 | `feat(web): add multi-stage dockerfile with nginx` |
| **D-C1** | **服务编排** | 编写 `docker-compose.yml`，同时启动前端、后端和 Redis | `feat(deploy): add docker-compose for fullstack orchestration` |

---

## 💾 第二部分：持久化与记忆 (Persistence)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **D-S1** | **Agent 持久化** | 在 `graph.py` 引入 `SqliteSaver` 或 `PostgresSaver` | `feat(agent): add persistent checkpointer for trip history` |
| **D-S2** | **状态恢复测试** | 验证容器重启后，之前的计划请求 ID 依然可以查询结果 | `test(deploy): verify state persistence across restarts` |

---

## 🧪 第三部分：自动化验证 (Validation)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **D-V1** | **集成测试脚本** | 编写 `tests/production_ready_test.py` 自动测试 API 端点 | `test: add production readiness integration tests` |
| **D-V2** | **安全扫描** | 检查 Docker 镜像体积及是否存在敏感信息泄露 | `chore: perform image security and size audit` |

---

## 🚦 执行准则 (Guidelines)

### ✅ 任务 (Do)
*   **前端 Proxy**: Nginx 需配置反向代理，将前端的 `/api` 请求转发给后端的 8000 端口，解决生产环境跨域。
*   **资源限制**: 在 Docker Compose 中限制容器内存（如 512MB），防止 OOM。
*   **健康检查**: 为 Docker 容器增加 `healthcheck` 指令。

### ❌ 禁忌 (Do Not)
*   不要在 Dockerfile 中 COPY `.env` 文件。
*   不要以 `root` 用户身份在容器内运行后端进程。

### ⚠️ 约束 (Constraints)
*   线上部署环境通常是 Linux，需确保 Python 依赖中没有 Darwin (macOS) 特有包。

### 📈 成功指标 (Success Signals)
*   只需运行 `docker-compose up`，即可在浏览器通过 80 端口访问完整的旅行助手。
*   生成的旅行计划 ID 存储在本地数据库文件中。
