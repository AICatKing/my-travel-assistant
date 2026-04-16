import sys
import os
from pathlib import Path

# 强制将 src 目录加入系统路径，确保导入 agent 不会出错
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

print(f">>>> [System] Python Path: {sys.path}")
print(f">>>> [System] Working Directory: {os.getcwd()}")

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
    from fastapi.staticfiles import StaticFiles
    import time
    import json
    import asyncio
    import uuid
    from typing import Any, Dict, AsyncGenerator

    # 导入 Agent 核心组件
    print(">>>> [System] 正在加载 Agent 逻辑...")
    from agent.graph import graph
    from agent.models import TripPlanRequest, TripPlan
    print(">>>> [System] Agent 逻辑加载成功")
except Exception as e:
    print(f">>>> [Critical Error] 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

app = FastAPI(
    title="My Travel Assistant API",
    version="0.1.0"
)

# 状态映射表
NODE_STATUS_MAP = {
    "search_attractions": "🗺️ 正在搜寻目的地热门景点并抓取精美图片...",
    "search_hotels": "🏨 正在为您筛选优质酒店住宿...",
    "query_weather": "🌤️ 正在查询目的地未来天气预报...",
    "planner": "📝 正在为您精心规划每一天的行程细节..."
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "online", "timestamp": int(time.time())}

@app.post("/api/plan/stream")
async def create_trip_plan_stream(request: TripPlanRequest):
    request_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": request_id}}
    
    async def event_generator() -> AsyncGenerator[str, None]:
        initial_state = {
            "city": request.city,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "days": request.days,
            "preferences": request.preferences,
            "budget": request.budget,
            "transportation": request.transportation,
            "accommodation": request.accommodation,
            "attractions": [],
            "hotels": [],
            "weather": [],
            "final_plan": None,
            "errors": []
        }

        try:
            async for chunk in graph.astream(initial_state, config=config, stream_mode="updates"):
                node_name = list(chunk.keys())[0]
                status_msg = NODE_STATUS_MAP.get(node_name)
                if status_msg:
                    yield f"data: {json.dumps({'type': 'status', 'content': status_msg}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.5)

            final_state = await graph.ainvoke(None, config=config)
            
            if final_state.get("errors"):
                yield f"data: {json.dumps({'type': 'error', 'content': final_state['errors'][0]}, ensure_ascii=False)}\n\n"
            else:
                final_plan = final_state.get("final_plan")
                if final_plan:
                    yield f"data: {json.dumps({'type': 'final', 'content': final_plan.dict()}, ensure_ascii=False)}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'content': '未能生成计划数据'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

frontend_dist_dir = Path(__file__).resolve().parents[2] / "web" / "dist"

if frontend_dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist_dir), html=True), name="frontend")
else:
    @app.get("/")
    async def root_fallback():
        return {"status": "online", "timestamp": int(time.time())}

if __name__ == "__main__":
    import uvicorn
    # 优先使用 Railway 提供的 PORT 变量，默认为 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
