from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from typing import Any, Dict

# 导入 Agent 核心组件
from agent.graph import graph
from agent.models import TripPlanRequest, TripPlan

app = FastAPI(
    title="My Travel Assistant API",
    description="Backend API for travel planning and recommendations",
    version="0.1.0"
)

# 配置 CORS 允许前端跨域访问 (P0 阶段允许所有源)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    """基础健康检查，确认 API 存活"""
    return {
        "status": "online",
        "timestamp": int(time.time()),
        "message": "Travel Assistant API is running"
    }

@app.post("/api/plan", response_model=TripPlan)
async def create_trip_plan(request: TripPlanRequest):
    """
    接收用户偏好请求，运行 LangGraph Agent 逻辑并返回最终生成的旅行计划。
    """
    print(f"\n>>>> [API Request] 收到旅行计划请求: {request.city} ({request.days}天)")
    
    # 构造 Agent 初始状态
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
        # 运行异步图逻辑
        # 注：ainvoke 是异步调用
        result = await graph.ainvoke(initial_state)
        
        # 检查是否有错误返回
        if result.get("errors"):
            print(f">>>> [API Error] Agent 返回错误: {result['errors']}")
            raise HTTPException(status_code=500, detail=result["errors"][0])
        
        final_plan = result.get("final_plan")
        if not final_plan:
            print(">>>> [API Error] Agent 未能生成最终计划。")
            raise HTTPException(status_code=500, detail="Failed to generate a trip plan.")
            
        print(f">>>> [API Success] 旅行计划生成成功！")
        return final_plan
        
    except Exception as e:
        print(f">>>> [API Exception] 发生意外错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 这里用于本地直接 python 运行调试
    uvicorn.run(app, host="0.0.0.0", port=8000)
