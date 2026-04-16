"""智能旅行助手 Graph 核心逻辑 - 真实数据版。
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from agent.models import (
    TripPlan,
    TripPlanRequest,
    Attraction,
    Hotel,
    WeatherInfo,
    Location,
    DayPlan,
    Meal,
    Budget,
    Context
)
from agent.tools import (
    search_amap_poi,
    get_amap_weather,
    parse_poi_to_attraction,
    parse_poi_to_hotel
)

load_dotenv()

class AgentState(TypedDict):
    """图的状态定义"""
    request: TripPlanRequest
    attractions: List[Attraction]
    hotels: List[Hotel]
    weather: List[WeatherInfo]
    final_plan: Optional[TripPlan]
    errors: List[str]

# --- 初始化 LLM ---
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    max_tokens=4000,
    temperature=0.3
)

parser = PydanticOutputParser(pydantic_object=TripPlan)

# --- 真实节点函数 (Real Nodes) ---

async def search_attractions_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """使用 AI 辅助生成关键词并调用高德搜索景点"""
    req = state['request']
    key = os.getenv("AMAP_API_KEY")
    print(f"--- [Debug] 开始搜索节点，Key 长度: {len(key) if key else 0} ---")
    print(f"--- [Amap] 正在搜索 {req.city} 的 {req.preferences} 景点 ---")
    
    # 1. 让 AI 建议搜索关键词
    prompt = f"针对{req.city}的{req.preferences}旅行偏好，请给出1个最核心的景点搜索关键词。仅返回关键词。"
    res = await llm.ainvoke(prompt)
    keywords = res.content.strip().replace("。", "").replace(".", "")
    print(f"--- [Debug] AI 建议关键词: {keywords} ---")
    
    # 2. 调用高德
    pois = search_amap_poi(keywords, req.city, types="050000") # 风景名胜的编码是 050000
    print(f"--- [Debug] 高德返回 POI 数量: {len(pois)} ---")
    
    # 3. 转换模型
    attractions = [parse_poi_to_attraction(p) for p in pois]
    return {"attractions": attractions}


async def search_hotels_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """搜索酒店"""
    req = state['request']
    print(f"--- [Amap] 正在搜索 {req.city} 的 {req.accommodation} ---")
    
    # 调用高德搜索酒店
    pois = search_amap_poi(req.accommodation, req.city, types="住宿服务")
    
    hotels = [parse_poi_to_hotel(p) for p in pois]
    return {"hotels": hotels}


async def query_weather_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """查询真实天气"""
    req = state['request']
    print(f"--- [Amap] 正在查询 {req.city} 的天气预报 ---")
    
    weather = get_amap_weather(req.city)
    return {"weather": weather}


async def planner_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Planner 保持不变，它依然负责整合"""
    print("--- [DeepSeek] 正在整合真实行程规划... ---")
    
    req = state['request']
    format_instructions = parser.get_format_instructions()
    
    # 增加安全性：如果没搜到东西，给点提示
    if not state['attractions']:
        return {"errors": ["未能搜寻到相关景点，请检查城市名或 API Key"]}

    prompt = f"""你是一位专业的旅行规划专家。

**用户需求**:
- 城市: {req.city}
- 日期: {req.start_date} 至 {req.end_date}
- 偏好: {req.preferences}
- 预算: {req.budget}
- 交通: {req.transportation}
- 住宿: {req.accommodation}

**真实素材**:
- 景点数据: {[a.dict() for a in state['attractions']]}
- 酒店数据: {[h.dict() for h in state['hotels']]}
- 天气数据: {[w.dict() for w in state['weather']]}

**任务**:
请将这些真实的素材整合成一份完整的旅行计划。

{format_instructions}

请直接输出 JSON，不要包含任何 markdown 标记。
"""

    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        if content.startswith("```json"): content = content[7:]
        if content.endswith("```"): content = content[:-3]
        
        final_plan = parser.parse(content)
        return {"final_plan": final_plan}
    except Exception as e:
        print(f"AI 生成计划失败: {e}")
        return {"errors": [str(e)]}

# --- 构建 Graph ---
workflow = StateGraph(AgentState, context_schema=Context)

workflow.add_node("search_attractions", search_attractions_node)
workflow.add_node("search_hotels", search_hotels_node)
workflow.add_node("query_weather", query_weather_node)
workflow.add_node("planner", planner_node)

workflow.add_edge(START, "search_attractions")
workflow.add_edge(START, "search_hotels")
workflow.add_edge(START, "query_weather")
workflow.add_edge("search_attractions", "planner")
workflow.add_edge("search_hotels", "planner")
workflow.add_edge("query_weather", "planner")
workflow.add_edge("planner", END)

graph = workflow.compile(name="Real Data Travel Assistant")
