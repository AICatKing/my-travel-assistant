# 任务 P1-C：高德地图可视化执行清单

**目标**: 在 UI 右侧引入交互式地图，直观展示景点分布及每日行程路线。

---

## 🔵 前端地图开发 (Frontend)

| 任务 ID | 任务描述 | 颗粒度/标准 | 提交记录建议 (Commit Message) |
| :--- | :--- | :--- | :--- |
| **MV-F1** | **依赖安装与配置** | 安装 `@amap/amap-jsapi-loader`，配置 JS API 安全密钥 | `feat(web): add amap jsapi loader dependency` |
| **MV-F2** | **地图容器组件** | 在 `App.vue` 或独立组件中初始化地图容器，支持响应式高度 | `feat(web): init amap container in ui` |
| **MV-F3** | **地理打点逻辑** | 根据 `TripPlan` 中的坐标，在地图上绘制景点 Marker | `feat(web): add markers for attractions and hotels` |
| **MV-F4** | **行程轨迹绘制** | 使用 `AMap.Polyline` 绘制每日景点的连接路线 | `feat(web): draw travel route polyline` |
| **MV-F5** | **自动视野调整** | 调用 `setFitView()` 确保所有打点和路线都在当前视野内 | `feat(web): auto adjust map view to fit markers` |
| **MV-F6** | **UI 布局重构** | 调整为左右/上下分栏布局，确保地图在滚动时保持可见（Sticky/Fixed） | `style(web): optimize layout for split map view` |

---

## 🚦 执行准则 (Guidelines)

### ✅ 任务 (Do)
*   **安全密钥**: 必须在前端正确配置 `_AMapSecurityConfig`（虽然 P0 阶段可以明文，但建议提示用户生产环境风险）。
*   **按需加载**: 仅加载 `AMap.Marker` 和 `AMap.Polyline` 等必要插件。
*   **清理逻辑**: 在组件卸载或重新生成计划时，必须清除旧的 Marker 和线段。

### ❌ 禁忌 (Do Not)
*   不要在每次状态更新（SSE status）时重画地图，仅在获取到最终计划或每日计划时绘制。
*   不要在前端硬编码地图 Key（应从环境变量获取，或在本地调试中使用占位符）。

### ⚠️ 约束 (Constraints)
*   高德 JS API 2.0 需要 `Key` 和 `安全密钥`（Security Code）双重认证。

### 📈 成功指标 (Success Signals)
*   页面右侧出现高德地图。
*   生成的西安行程中，大雁塔、兵马俑等景点在地图上精准打点，并由线条连接。
