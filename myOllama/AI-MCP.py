from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
import asyncio
import json

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"


async def fetch_latest_docs(library: str, topic: str = None):
    """通过 Context7 获取最新文档"""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp@latest"]
    )

    async with ClientSession(server_params) as session:
        await session.initialize()

        query = f"{library} {topic}" if topic else library
        result = await session.call_tool(
            "get_documentation",
            arguments={"query": query}
        )
        return result.content


def ask_with_context7(question: str):
    """自动判断是否需要查询最新文档"""

    # 检测是否涉及特定框架/库
    libraries = ["nextjs", "react", "vue", "langchain", "fastapi", "django"]
    mentioned_libs = [lib for lib in libraries if lib.lower() in question.lower()]

    context = ""
    if mentioned_libs:
        print(f"📚 检测到涉及 {mentioned_libs}，正在查询最新文档...")
        for lib in mentioned_libs:
            docs = asyncio.run(fetch_latest_docs(lib))
            context += f"\n【{lib} 最新文档】\n{docs}\n"

    # 构建最终提示词
    if context:
        prompt = f"""{context}

【用户问题】
{question}

请基于以上最新文档信息回答。如果文档信息与你的知识有冲突，以文档为准。"""
    else:
        prompt = question

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )

    return response.choices[0].message.content


# 使用示例
answer = ask_with_context7("Next.js 15 的 Server Components 怎么用？")
print(answer)