"""智能旅行助手 Graph 核心逻辑 - 异步优化版。
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
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
    parse_poi_to_hotel,
    search_unsplash_image
)

# 生产环境环境变量加载
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

# --- 核心：按需初始化 LLM ---
def get_model():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # 这里抛出具体的运行时错误，而不是导入错误
        raise ValueError("环境变量 DEEPSEEK_API_KEY 未设置")
    
    return ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=api_key,
        openai_api_base="https://api.deepseek.com",
        max_tokens=4000,
        temperature=0.3
    )

parser = PydanticOutputParser(pydantic_object=TripPlan)

# --- 节点函数 ---

async def search_attractions_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 search_attractions_node")
    try:
        llm = get_model()
        city = state.get('city', "北京")
        prefs = state.get('preferences', "历史文化")
        
        prompt = f"针对{city}的{prefs}旅行偏好，请给出1个最核心的景点搜索关键词。仅返回关键词。"
        res = await llm.ainvoke(prompt)
        keywords = res.content.strip().replace("。", "").replace(".", "")
        
        pois = await asyncio.to_thread(search_amap_poi, keywords, city, "050000")
        attractions = [parse_poi_to_attraction(p) for p in pois]

        async def fetch_img(attr: Attraction):
            img_url = await asyncio.to_thread(search_unsplash_image, f"{city} {attr.name}")
            attr.image_url = img_url

        if attractions:
            await asyncio.gather(*(fetch_img(a) for a in attractions))

        return {"attractions": attractions}
    except Exception as e:
        return {"errors": [f"景点搜索阶段失败: {str(e)}"]}


async def search_hotels_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 search_hotels_node")
    try:
        city = state.get('city', "北京")
        acc = state.get('accommodation', "高档酒店")
        
        pois = await asyncio.to_thread(search_amap_poi, acc, city, "住宿服务")
        hotels = [parse_poi_to_hotel(p) for p in pois]

        async def fetch_hotel_img(h: Hotel):
            img_url = await asyncio.to_thread(search_unsplash_image, f"{city} {h.name}")
            h.image_url = img_url

        if hotels:
            await asyncio.gather(*(fetch_hotel_img(h) for h in hotels))

        return {"hotels": hotels}
    except Exception as e:
        return {"errors": [f"酒店搜索阶段失败: {str(e)}"]}


async def query_weather_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 query_weather_node")
    city = state.get('city', "北京")
    weather = await asyncio.to_thread(get_amap_weather, city)
    return {"weather": weather}


async def planner_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("\n>>>> [Node] 进入 planner_node")
    
    if not state.get('attractions'):
        return {"errors": ["未能搜寻到相关景点，请检查城市名"]}

    try:
        llm = get_model()
        prompt = f"""你是一位专业的旅行规划专家。
城市: {state['city']}
日期: {state['start_date']} 至 {state['end_date']}
景点: {[a.dict() for a in state['attractions']]}
酒店: {[h.dict() for h in state['hotels']]}
天气: {[w.dict() for w in state['weather']]}

{parser.get_format_instructions()}
直接输出 JSON。
"""
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        if content.startswith("```json"): content = content[7:]
        if content.endswith("```"): content = content[:-3]
        
        final_plan = parser.parse(content)
        return {"final_plan": final_plan}
    except Exception as e:
        return {"errors": [f"规划生成失败: {str(e)}"]}

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

memory = MemorySaver()

graph = workflow.compile(
    checkpointer=memory,
    name="Real Data Travel Assistant"
)
