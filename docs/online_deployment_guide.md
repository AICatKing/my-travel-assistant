# 智能旅行助手：线上部署实操手册 (Zeabur 版)

本手册指导如何将容器化后的项目一键部署至公网环境。

## 1. 代码准备
1. 确保所有本地变更已提交并推送到 GitHub 仓库。
2. 检查 `.gitignore` 确保 `.env` 没有被误传（安全第一）。

## 2. Zeabur 部署步骤
Zeabur 会自动识别根目录的 `docker-compose.yml`。

1. **登录 Zeabur**: 使用 GitHub 账号登录 [zeabur.com](https://zeabur.com)。
2. **创建项目**: 点击 `Create Project` -> `Deploy New Service` -> `GitHub`。
3. **选择仓库**: 选择 `my-travel-assistant`。
4. **自动构建**: Zeabur 会检测到 Docker 配置：
   * 它会同时启动 `backend` 和 `frontend` 两个容器。
5. **配置环境变量 (关键)**:
   * 进入 `backend` 服务的 `Variables` 界面，手动添加：
     * `DEEPSEEK_API_KEY`
     * `AMAP_API_KEY`
     * `UNSPLASH_ACCESS_KEY`
     * `DB_PATH` = `/data/checkpoints.db` (可选)
6. **配置存储 (可选)**:
   * 为 `backend` 增加一个挂载路径 `/data`，类型为 `Persistent Volume`。
7. **暴露域名**:
   * 在 `frontend` 服务的 `Networking` 界面，点击 `Generate Domain`。
   * 你将得到一个类似 `travel-assistant.zeabur.app` 的公网地址。

## 3. 生产环境优化建议

### (1) 安全性增强
在 `src/api/main.py` 中限制 CORS：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.zeabur.app"], # 替换为你的真实域名
    ...
)
```

### (2) 前端 API 地址
我们在 `web/src/api.ts` 中已经写了：
```typescript
const API_BASE_URL = import.meta.env.MODE === 'production' ? '/api' : 'http://localhost:8000/api';
```
这确保了在线上环境下，前端会自动通过 Nginx 的反向代理访问后端，而不会尝试去连接用户本地的 `localhost:8000`。

## 4. 验证线上环境
访问生成的域名，尝试进行一次规划。
* **状态流式输出 (SSE)**: 由于我们在 Nginx 配置中关闭了 `proxy_buffering`，线上环境依然能看到逐句跳出的进度提示。
* **地图渲染**: 确保高德地图的 `Key` 已绑定了你的线上域名（在高德开发者后台配置白名单）。
