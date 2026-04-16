# FastAPI 集成指南：从 Agent 到 Web 服务

本手册指导如何将现有的 LangGraph 智能体逻辑通过 FastAPI 暴露为生产级的 Web 接口。

## 1. 推荐目录结构

建议在 `src/` 下新增 `api/` 目录，保持逻辑清晰：

```text
my-travel-assistant/
├── src/
│   ├── agent/          # 核心智能体逻辑 (已存在)
│   │   ├── graph.py    # LangGraph 定义
│   │   └── models.py   # Pydantic 模型
│   └── api/            # 新增：FastAPI 后端层
│       ├── __init__.py
│       ├── main.py     # 程序入口
│       └── routes.py   # 路由定义
├── .env                # 共享环境变量
└── pyproject.toml      # 共享依赖管理
```

## 2. 核心集成逻辑 (src/api/main.py)

FastAPI 的核心任务是接收前端的 JSON 请求，并驱动 `graph.py` 中的 `workflow`。

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.graph import graph  # 直接引用现有的图逻辑
from agent.models import TripPlanRequest, TripPlan

app = FastAPI(title="Travel Assistant API")

# 解决跨域问题，允许 Vue3 前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/plan", response_model=TripPlan)
async def create_trip_plan(request: TripPlanRequest):
    """
    接收用户偏好，运行 Agent 图逻辑并返回最终计划
    """
    try:
        # 将请求转换为 Agent 初始状态
        initial_state = {
            "city": request.city,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "days": request.days,
            "preferences": request.preferences,
            "budget": request.budget,
            "accommodation": request.accommodation,
            "attractions": [],
            "hotels": [],
            "weather": []
        }
        
        # 运行 LangGraph (invoke 是同步/异步兼容的)
        result = await graph.ainvoke(initial_state)
        
        if result.get("errors"):
            raise HTTPException(status_code=500, detail=result["errors"][0])
            
        return result["final_plan"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 3. 核心步骤

### 第一步：安装依赖
在项目根目录运行：
```bash
uv add fastapi uvicorn
```

### 第二步：环境变量共享
FastAPI 会自动读取根目录的 `.env`。确保你的 `AMAP_API_KEY` 和 `DEEPSEEK_API_KEY` 已正确配置。

### 第三步：支持流式输出 (SSE) - 进阶建议
对于 AI 应用，用户不喜欢盯着转圈圈。你可以使用 FastAPI 的 `StreamingResponse` 结合 LangGraph 的 `astream` 方法：
*   前端可以实时看到：“正在搜寻上海景点...”、“正在查询天气...”
*   这能显著降低用户的“感知等待时间”。

## 4. 为什么这样做？
1. **类型安全**：API 直接使用 `src/agent/models.py` 里的 `TripPlanRequest`，前端发错字段后端会自动拦截。
2. **文档同步**：运行 FastAPI 后，访问 `/docs` 即可自动生成 Swagger 文档，前端开发看着文档就能对接。
3. **低耦合**：Agent 的核心逻辑依然在 `agent/` 目录下，你可以随时通过 `test_run.py` 调试它，而不必启动 Web 服务器。
