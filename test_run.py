import asyncio
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

    # 2. 构造初始状态
    initial_state = {
        "request": user_request,
        "attractions": [],
        "hotels": [],
        "weather": [],
        "final_plan": None,
        "errors": []
    }

    print("=== 开始运行智能旅行助手 (Mock模式) ===")
    
    # 3. 运行 Graph
    # 注意：我们使用 ainvoke 因为节点是异步的
    result = await graph.ainvoke(initial_state)

    # 4. 打印结果
    print("\n=== 运行完成 ===")
    plan = result.get("final_plan")
    if plan:
        print(f"目的地: {plan.city}")
        print(f"总体建议: {plan.overall_suggestions}")
        print(f"第一天行程: {plan.days[0].description}")
        print(f"预估总预算: {plan.budget.total} 元")
    else:
        print("未生成计划。")

if __name__ == "__main__":
    asyncio.run(main())
