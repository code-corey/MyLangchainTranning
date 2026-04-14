from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import os

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# 初始化百炼（DashScope）的 OpenAI 兼容模式大模型
# 请确保环境变量中已设置 DASHSCOPE_API_KEY
llm = ChatOpenAI(
    model="qwen3-vl-flash-2026-01-22", # 也可以使用 qwen-max, qwen-turbo 等
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

agent = create_agent(
    model=llm, # 这里直接传入实例化的 LLM 对象
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
print(agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
))