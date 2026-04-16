"""智能旅行助手 Graph 核心逻辑 - 混合模式 (DeepSeek 兼容版)。
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

load_dotenv()

class AgentState(TypedDict):
    """图的状态定义"""
    request: TripPlanRequest
    attractions: List[Attraction]
    hotels: List[Hotel]
    weather: List[WeatherInfo]
    final_plan: Optional[TripPlan]
    errors: List[str]

# --- 初始化 DeepSeek ---
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    max_tokens=4000,
    temperature=0.7 # 稍微提高多样性
)

# 定义解析器
parser = PydanticOutputParser(pydantic_object=TripPlan)

# --- 模拟节点保持不变 ---

async def search_attractions_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    city = state['request'].city
    print(f"--- [Mock] 正在搜索 {city} 的景点 ---")
    mock_attractions = [
        Attraction(name="故宫博物院", address="北京市东城区景山前街4号", location=Location(longitude=116.397, latitude=39.916), visit_duration=240, description="皇家宫殿，木质结构古建筑。", ticket_price=60),
        Attraction(name="天坛公园", address="北京市东城区天坛路", location=Location(longitude=116.407, latitude=39.881), visit_duration=120, description="祭天场所。", ticket_price=35),
        Attraction(name="颐和园", address="北京市海淀区新建宫门路19号", location=Location(longitude=116.273, latitude=39.999), visit_duration=180, description="皇家园林，长廊、石舫。", ticket_price=30)
    ]
    return {"attractions": mock_attractions}

async def search_hotels_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print(f"--- [Mock] 正在搜索 {state['request'].city} 的酒店 ---")
    mock_hotels = [
        Hotel(name="北京王府井希尔顿酒店", address="北京东城区王府井东安门大街88号", location=Location(longitude=116.411, latitude=39.914), price_range="1500", rating="4.8", estimated_cost=1500)
    ]
    return {"hotels": mock_hotels}

async def query_weather_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print(f"--- [Mock] 正在查询 {state['request'].city} 的天气 ---")
    mock_weather = [
        WeatherInfo(date="2026-04-16", day_weather="晴", night_weather="多云", day_temp=22, night_temp=12, wind_direction="北风", wind_power="3级"),
        WeatherInfo(date="2026-04-17", day_weather="多云", night_weather="阴", day_temp=20, night_temp=14, wind_direction="南风", wind_power="2级")
    ]
    return {"weather": mock_weather}

# --- 改进后的 Planner 节点 ---

async def planner_node(state: AgentState, runtime: Runtime[Context]) -> Dict[str, Any]:
    print("--- [DeepSeek] 正在整合行程规划... ---")
    
    req = state['request']
    
    # 将 Pydantic 对象的描述注入到 Prompt 中
    format_instructions = parser.get_format_instructions()
    
    prompt = f"""你是一位专业的旅行规划专家。

**用户需求**:
- 城市: {req.city}
- 日期: {req.start_date} 至 {req.end_date}
- 偏好: {req.preferences}
- 预算: {req.budget}
- 交通: {req.transportation}
- 住宿: {req.accommodation}

**素材**:
- 景点: {[a.dict() for a in state['attractions']]}
- 酒店: {[h.dict() for h in state['hotels']]}
- 天气: {[w.dict() for w in state['weather']]}

**任务**:
请将这些素材整合成一份完整的旅行计划。

{format_instructions}

请直接输出 JSON，不要包含任何 markdown 标记（如 ```json ）。
"""

    try:
        response = await llm.ainvoke(prompt)
        # 清理可能存在的 markdown 标记
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        final_plan = parser.parse(content)
        return {"final_plan": final_plan}
    except Exception as e:
        print(f"AI 生成计划失败: {e}")
        # 如果解析失败，打印原始内容便于调试
        if 'response' in locals():
            print(f"AI 原始输出: {response.content}")
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

graph = workflow.compile(name="Travel Assistant DeepSeek Compatibility Graph")
