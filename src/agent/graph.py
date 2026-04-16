"""智能旅行助手 Graph 核心逻辑 - 异步优化版。

修复了 LangGraph Studio 中 requests 导致的 Blocking call 报错。
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, List, Optional
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
    city: str
    start_date: str
    end_date: str
    days: int
    preferences: str
    budget: str
    transportation: str
    accommodation: str
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

# --- 节点函数 (使用 asyncio.to_thread) ---

async def search_attractions_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 search_attractions_node")
    city = state.get('city', "北京")
    prefs = state.get('preferences', "历史文化")
    
    # 1. AI 建议关键词
    prompt = f"针对{city}的{prefs}旅行偏好，请给出1个最核心的景点搜索关键词。仅返回关键词。"
    res = await llm.ainvoke(prompt)
    keywords = res.content.strip().replace("。", "").replace(".", "")
    print(f">>>> [Debug] AI 建议关键词: {keywords}")
    
    # 2. 调用高德 (通过 to_thread 解决阻塞问题)
    pois = await asyncio.to_thread(search_amap_poi, keywords, city, "050000")
    print(f">>>> [Debug] 高德返回 POI 数量: {len(pois)}")
    
    attractions = [parse_poi_to_attraction(p) for p in pois]
    return {"attractions": attractions}


async def search_hotels_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 search_hotels_node")
    city = state.get('city', "北京")
    acc = state.get('accommodation', "高档酒店")
    
    # 通过 to_thread 运行同步函数
    pois = await asyncio.to_thread(search_amap_poi, acc, city, "住宿服务")
    print(f">>>> [Debug] 高德返回酒店数量: {len(pois)}")
    
    hotels = [parse_poi_to_hotel(p) for p in pois]
    return {"hotels": hotels}


async def query_weather_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 query_weather_node")
    city = state.get('city', "北京")
    
    # 通过 to_thread 运行同步函数
    weather = await asyncio.to_thread(get_amap_weather, city)
    print(f">>>> [Debug] 获取天气天数: {len(weather)}")
    return {"weather": weather}


async def planner_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 planner_node")
    
    if not state.get('attractions'):
        print(">>>> [Error] Planner 发现景点列表为空！")
        return {"errors": ["未能搜寻到相关景点，请检查城市名"]}

    prompt = f"""你是一位专业的旅行规划专家。
城市: {state['city']}
日期: {state['start_date']} 至 {state['end_date']}
景点: {[a.dict() for a in state['attractions']]}
酒店: {[h.dict() for h in state['hotels']]}
天气: {[w.dict() for w in state['weather']]}

{parser.get_format_instructions()}
直接输出 JSON。
"""
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        if content.startswith("```json"): content = content[7:]
        if content.endswith("```"): content = content[:-3]
        
        final_plan = parser.parse(content)
        print(">>>> [Success] 计划生成成功！")
        return {"final_plan": final_plan}
    except Exception as e:
        print(f">>>> [Error] AI 生成失败: {e}")
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
