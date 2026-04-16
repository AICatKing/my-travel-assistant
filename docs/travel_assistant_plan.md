# 智能旅行助手开发计划书 (基于 LangGraph)

本项目旨在参考《HelloAgents》教程，利用 LangGraph 框架构建一个功能完备的智能旅行助手。

## 1. 核心目标
实现一个能够根据用户目的地、日期、偏好和预算，自动生成包含景点、酒店、天气和预算明细的结构化行程规划工具。

## 2. 系统架构设计

### 2.1 状态管理 (State)
在 LangGraph 中，我们将维护一个全局状态，记录以下信息：
- 用户原始请求 (Request)
- 搜索到的景点列表 (Attractions)
- 推荐的酒店列表 (Hotels)
- 天气预报信息 (Weather)
- 最终生成的旅行计划 (Final Plan)

### 2.2 节点设计 (Nodes)
- **search_attractions**: 调用高德地图 API 搜索符合偏好的景点。
- **search_hotels**: 调用高德地图 API 根据预算搜索酒店。
- **query_weather**: 查询目的地在旅行期间的天气。
- **planner**: 汇总以上所有信息，利用大模型生成每日详细行程及预算。

### 2.3 工具集成 (Tools)
- **Amap MCP**: 用于所有地理位置相关的查询。
- **Unsplash Service**: 为行程中的景点匹配精美图片。

## 3. 分阶段路线图

### 第一阶段：基础构建 (当前阶段)
1.  **环境配置**: 设置 API Keys (OpenAI/DeepSeek, Amap, Unsplash)。
2.  **数据建模**: 使用 Pydantic 定义 `TripPlan`、`DayPlan`、`Attraction` 等核心数据结构。

### 第二阶段：工具与 Agent 开发
1.  **MCP 集成**: 配置并测试高德地图 MCP 服务。
2.  **节点实现**: 编写各个 Agent 节点的 Python 函数，确保它们能正确调用工具并更新 State。

### 第三阶段：Graph 编排与调试
1.  **图定义**: 在 `graph.py` 中连接节点，实现并行搜索逻辑（提高效率）。
2.  **提示词优化**: 优化 Planner 的 System Prompt，确保输出稳定的 JSON 格式。
3.  **Studio 调试**: 在 LangGraph Studio 中观察执行流。

### 第四阶段：UI 与 交互 (进阶)
1.  **API 暴露**: 确保 LangGraph Server 正常运行。
2.  **前端实现**: 构建 Vue3 界面，展示地图、行程卡片和预算图表。

---

## 4. 待办清单 (Todo List)
- [ ] 定义 Pydantic 数据模型
- [ ] 配置环境变量
- [ ] 集成高德地图工具
- [ ] 编写 Graph 节点逻辑
- [ ] 运行并验证第一个行程生成
