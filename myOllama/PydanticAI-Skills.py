from pydantic_ai import Agent
from openai import AsyncOpenAI

# 桥接你的本地服务
client = AsyncOpenAI(base_url="http://192.168.13.23:8842/v1", api_key="ollama")

agent = Agent(
    model='openai:Qwen3.5-27B-Q8_0.gguf',
    fallback_raw_client=client # 强制使用你的本地客户端
)

@agent.tool
async def get_weather(city: str) -> str:
    """获取指定城市的实时天气。"""
    return f"{city}今天晴，25°C"

# 运行后模型会自动识别并调用这个 Skill