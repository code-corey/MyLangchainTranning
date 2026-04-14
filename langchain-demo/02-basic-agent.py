import os
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy


# 定义系统提示词
SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.

IMPORTANT: You MUST always provide your final answer by calling the ResponseFormat tool. 
Do not respond with normal text; use the structured output format provided

"""

# 定义上下文 Schema
@dataclass
class Context:
    """自定义运行时上下文 Schema。"""
    user_id: str

# 定义工具
@tool
def get_weather_for_location(city: str) -> str:
    """获取指定城市的天气。"""
    return f"It's always sunny in {city}!"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据 user_id 获取用户所在地。"""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"


model = ChatOpenAI(
    model="qwen3-vl-flash-2026-01-22", # 也可以使用 qwen-max, qwen-turbo 等
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# 定义结构化输出格式
@dataclass
class ResponseFormat:
    """智能体的响应 Schema。"""
    # 双关语风格的回复（必填）
    punny_response: str
    # 任何有趣的天气信息（可选）
    weather_conditions: str | None = None

# 设置记忆（用于多轮对话）
checkpointer = InMemorySaver()

# 创建智能体
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)

# 运行智能体
# thread_id 是一段对话的唯一标识
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather outside?"}]},
    config=config,
    context=Context(user_id="1")
)

print("第一次 structured_response：")
print(response["structured_response"])
print("第一次完整返回（含 messages 等）：")
print(response)
# ResponseFormat(
#     punny_response="Florida is still having a 'sun-derful' day! The sunshine is playing 'ray-dio' hits all day long! I'd say it's the perfect weather for some 'solar-bration'! If you were hoping for rain, I'm afraid that idea is all 'washed up' - the forecast remains 'clear-ly' brilliant!",
#     weather_conditions="It's always sunny in Florida!"
# )


# 继续使用同一个 thread_id，即可延续同一段对话的上下文
response = agent.invoke(
    {"messages": [{"role": "user", "content": "thank you!"}]},
    config=config,
    context=Context(user_id="1")
)

print("第二次 structured_response：")
print(response["structured_response"])
print("第二次完整返回（含 messages 等）：")
print(response)
# ResponseFormat(
#     punny_response="You're 'thund-erfully' welcome! It's always a 'breeze' to help you stay 'current' with the weather. I'm just 'cloud'-ing around waiting to 'shower' you with more forecasts whenever you need them. Have a 'sun-sational' day in the Florida sunshine!",
#     weather_conditions=None
# )
