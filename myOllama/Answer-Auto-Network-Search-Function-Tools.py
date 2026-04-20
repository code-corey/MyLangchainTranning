from openai import OpenAI
from ddgs import DDGS  # 注意：导入方式变了
import json

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"


# ========== 定义工具（搜索功能） ==========
def web_search(query: str, max_results: int = 3) -> str:
    """执行网络搜索，返回搜索结果"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return json.dumps({"error": "未找到搜索结果"})

        # 格式化结果
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", "")[:500],
                "url": r.get("href", "")
            })
        return json.dumps({"results": formatted}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}"})


# ========== 定义工具描述（告诉模型这个工具怎么用） ==========
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索网络获取最新信息。当用户询问实时新闻、天气、股价、或者任何需要最新数据的问题时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回结果数量，默认3条",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ========== 带工具调用的问答函数 ==========
def ask_with_tools(question: str, verbose: bool = True) -> str:
    """
    智能问答，模型自动判断是否需要调用搜索工具
    """
    messages = [
        {
            "role": "system",
            "content": "你是一个智能助手。如果你需要最新信息来回答用户问题，请调用 web_search 工具。"
        },
        {
            "role": "user",
            "content": question
        }
    ]

    if verbose:
        print(f"👤 用户: {question}")

    # 第一轮：让模型决定是否调用工具
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",  # 让模型自动决定是否调用工具
        temperature=0.7
    )

    message = response.choices[0].message

    # 检查模型是否想要调用工具
    if message.tool_calls:
        if verbose:
            print(f"🔧 模型决定调用工具...")

        # 执行工具调用
        for tool_call in message.tool_calls:
            if tool_call.function.name == "web_search":
                # 解析参数
                args = json.loads(tool_call.function.arguments)
                query = args.get("query")
                max_results = args.get("max_results", 3)

                if verbose:
                    print(f"   🔍 搜索: {query}")

                # 执行搜索
                search_result = web_search(query, max_results)

                # 将工具结果添加到消息历史
                messages.append(message)  # 添加模型的工具调用请求
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": search_result
                })

        # 第二轮：模型基于搜索结果生成最终回答
        if verbose:
            print(f"   📝 基于搜索结果生成回答...")

        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7
        )

        return final_response.choices[0].message.content
    else:
        # 模型不需要调用工具，直接返回
        if verbose:
            print(f"💬 模型直接回答（无需搜索）")
        return message.content


# ========== 使用示例 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 智能问答系统（Function Calling 自动联网）")
    print("=" * 60)

    # 示例1：需要搜索的问题
    print("\n【测试1】需要实时信息")
    print("-" * 40)
    answer = ask_with_tools("今天有什么重要的科技新闻？")
    print(f"\n🤖 回答:\n{answer}")

    print("\n" + "=" * 60)
