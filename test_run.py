import asyncio
import os
from agent.graph import graph
from agent.models import TripPlanRequest

async def main():
    # 1. 模拟用户输入
    user_request = TripPlanRequest(
        city="北京",
        start_date="2026-04-16",
        end_date="2026-04-18",
        days=3,
        preferences="历史文化",
        budget="中等",
        transportation="公共交通",
        accommodation="高档酒店"
    )

    initial_state = {
        "request": user_request,
        "attractions": [],
        "hotels": [],
        "weather": [],
        "final_plan": None,
        "errors": []
    }

    print("=== 开始运行智能旅行助手 (Real Data) ===")
    
    # 3. 运行 Graph
    result = await graph.ainvoke(initial_state)

    # 4. 调试输出：检查中间数据
    print(f"\n[Debug] 搜寻到的景点数量: {len(result.get('attractions', []))}")
    print(f"[Debug] 搜寻到的酒店数量: {len(result.get('hotels', []))}")
    print(f"[Debug] 获取到的天气天数: {len(result.get('weather', []))}")
    
    if result.get("errors"):
        print(f"[Debug] 运行中出现的错误: {result['errors']}")

    # 5. 打印最终结果
    print("\n=== 运行完成 ===")
    plan = result.get("final_plan")
    if plan:
        print(f"目的地: {plan.city}")
        print(f"总体建议: {plan.overall_suggestions}")
        print(f"第一天描述: {plan.days[0].description}")
        print("-" * 20)
        for day in plan.days:
            print(f"第 {day.day_index + 1} 天 ({day.date}):")
            for attr in day.attractions:
                print(f"  - 景点: {attr.name}")
        print("-" * 20)
        print(f"预估总预算: {plan.budget.total if plan.budget else '未知'} 元")
    else:
        print("未生成计划。请检查上面的调试信息。")

if __name__ == "__main__":
    asyncio.run(main())
