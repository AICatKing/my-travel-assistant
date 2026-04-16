# 任务 P1-A：Unsplash 视觉增强执行清单

**目标**: 为每个生成的景点自动配上高品质封面图，提升用户体感价值。

---

## 🟢 第一部分：后端工具与逻辑 (Backend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **UA-B1** | **Unsplash 工具开发** | 在 `tools.py` 新增 `search_unsplash_image(query)` 函数 | `feat(tools): add unsplash image search tool` |
| **UA-B2** | **模型扩展** | 确保 `Attraction` 和 `Hotel` 模型包含 `image_url` 字段 | `refactor(models): ensure image_url field in models` |
| **UA-B3** | **节点逻辑集成** | 在 `search_attractions` 节点中并行调用图片搜索，补全 URL | `feat(graph): integrate image fetching into attraction node` |
| **UA-B4** | **并发优化** | 使用 `asyncio.gather` 同时获取多个景点的图片，避免串行导致更慢 | `perf(agent): fetch multiple images in parallel` |
| **UA-B5** | **配置与安全** | 在 `.env.example` 增加 `UNSPLASH_ACCESS_KEY` 占位符 | `chore: add unsplash key to env template` |

---

## 🔵 第二部分：前端展示优化 (Frontend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **UA-F1** | **卡片样式升级** | 在 `App.vue` 中为景点增加图片容器，支持 `object-cover` | `feat(web): add image display support for attraction cards` |
| **UA-F2** | **占位图处理** | 实现图片加载失败时的优雅降级（展示默认风景图或颜色块） | `feat(web): add placeholder for missing images` |
| **UA-F3** | **布局调整** | 调整每日行程展示，将图片与文字描述进行左右或上下排布 | `style(web): optimize layout for image-heavy content` |

---

## 🚦 执行准则 (Guidelines)

### ✅ 任务 (Do)
*   **语义化搜索**: 搜索图片时使用 `城市 + 景点名称` 作为关键词，提高准确率。
*   **尺寸控制**: 仅请求 `small` 或 `regular` 尺寸的图片 URL，减轻前端加载压力。
*   **异常捕获**: 如果 Unsplash 报错或配额用完，后端应返回空字符串而非崩溃。

### ❌ 禁忌 (Do Not)
*   不要在循环中同步调用 API，必须使用 `asyncio.to_thread` 或 `httpx`。
*   不要下载图片到本地服务器，直接返回外链 URL。

### ⚠️ 约束 (Constraints)
*   Unsplash 免费版 API 限制为每小时 50 次请求，需在代码中加入简单的缓存或降级逻辑。

### 📈 成功指标 (Success Signals)
*   生成的西安旅行计划中，“西安城墙”下方出现一张真实且美观的高清照片。
*   后端处理总时长增加不超过 2 秒。
