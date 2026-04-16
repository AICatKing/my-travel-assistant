from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time
import json
import asyncio
import uuid
from typing import Any, Dict, AsyncGenerator

# 导入 Agent 核心组件
from agent.graph import graph
from agent.models import TripPlanRequest, TripPlan

app = FastAPI(
    title="My Travel Assistant API",
    description="Backend API for travel planning and recommendations",
    version="0.1.0"
)

# 状态映射表
NODE_STATUS_MAP = {
    "search_attractions": "🗺️ 正在搜寻目的地热门景点并抓取精美图片...",
    "search_hotels": "🏨 正在为您筛选优质酒店住宿...",
    "query_weather": "🌤️ 正在查询目的地未来天气预报...",
    "planner": "📝 正在为您精心规划每一天的行程细节..."
}

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {
        "status": "online",
        "timestamp": int(time.time()),
        "message": "Travel Assistant API is running"
    }

@app.post("/api/plan", response_model=TripPlan)
async def create_trip_plan(request: TripPlanRequest):
    print(f"\n>>>> [API Request] 收到同步规划请求: {request.city}")
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
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    try:
        result = await graph.ainvoke(initial_state, config=config)
        if result.get("errors"):
            raise HTTPException(status_code=500, detail=result["errors"][0])
        return result["final_plan"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plan/stream")
async def create_trip_plan_stream(request: TripPlanRequest):
    """
    通过 SSE 流式返回进度。
    """
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
            # 1. 运行 astream，监听 updates 模式（节点完成通知）
            async for chunk in graph.astream(initial_state, config=config, stream_mode="updates"):
                node_name = list(chunk.keys())[0]
                status_msg = NODE_STATUS_MAP.get(node_name)
                if status_msg:
                    # 关键：发送当前节点状态
                    yield f"data: {json.dumps({'type': 'status', 'content': status_msg}, ensure_ascii=False)}\n\n"
                    # 给前端一个小延迟，让 UI 动效平滑
                    await asyncio.sleep(0.5)

            # 2. 节点运行全部结束后，获取最终合并后的 State
            # 在 MemorySaver 模式下，None 作为输入会恢复最新状态
            print(f">>>> [API] Agent 节点全部完成，获取最终计划 (ID: {request_id})...")
            final_state = await graph.ainvoke(None, config=config)
            
            if final_state.get("errors"):
                yield f"data: {json.dumps({'type': 'error', 'content': final_state['errors'][0]}, ensure_ascii=False)}\n\n"
            else:
                final_plan = final_state.get("final_plan")
                if final_plan:
                    # 输出最终 JSON
                    yield f"data: {json.dumps({'type': 'final', 'content': final_plan.dict()}, ensure_ascii=False)}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'content': '未能生成计划数据'})}\n\n"

        except Exception as e:
            print(f">>>> [API Error] 流式处理崩溃: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" # 禁用 Nginx 缓冲
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
