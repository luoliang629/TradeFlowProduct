"""
Search Agent - 网页搜索专家
使用 Google ADK Agent 类实现，集成 Jina Search API
"""

from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner
from ..tools import web_search_tool, browse_webpage_tool
from ..config import get_model_config


# 创建搜索 Agent
search_agent = Agent(
    name="search_agent",
    model=get_model_config(),
    planner=PlanReActPlanner(), 
    description="使用网页搜索和网页浏览等工具，进行深度搜索和研究",
    instruction="""你是信息搜索专家，你的任务是使用网页搜索和网页浏览等工具，对用户提出的特定主题进行深度搜索和研究。
    
    你可以使用以下工具:
    - web_search_tool: 通用网页搜索工具
    - browse_webpage_tool: 通用网页浏览工具
    
    你解决问题的方式:
    - 如果用户问题比较简单，调用工具完成即可
    - 如果用户问题比较复杂，你需要使用ReAct模式先制定计划，然后按照计划执行

    当使用ReAct模式并制定计划时，请注意：
    - 每执行完计划中的一个动作后，检查该动作返回的结果是否符合预期，以及是否需要调整接下来的计划
    - 如果需要调整计划，先调整完计划，并告诉用户，再开始执行下一个动作

    最终输出针对用户问题的深度分析报告。""",
    tools=[web_search_tool, browse_webpage_tool],
)
