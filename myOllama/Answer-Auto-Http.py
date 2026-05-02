from openai import OpenAI
import requests
import json

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"


# ========== 工具1：通用HTTP请求 ==========
def http_request(url: str, method: str = "GET", headers: dict = None, body: dict = None) -> str:
    """
    执行HTTP请求，获取网络资源
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers or {}, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers or {}, json=body, timeout=10)
        else:
            return json.dumps({"error": f"不支持的方法: {method}"})

        # 限制返回长度，避免超出模型上下文
        content = response.text[:3000]
        return json.dumps({
            "status_code": response.status_code,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ========== 工具2：网页内容获取（专用于读取URL） ==========
def fetch_webpage(url: str) -> str:
    """
    获取指定网页的内容
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # 简单提取文本内容（实际可用BeautifulSoup优化）
        content = response.text[:4000]
        return json.dumps({
            "url": url,
            "status": response.status_code,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"获取失败: {str(e)}"})


# ========== 工具3：搜索功能（通过DuckDuckGo） ==========
def web_search(query: str, max_results: int = 3) -> str:
    """
    搜索网络获取最新信息
    """
    try:
        # 使用免费的DuckDuckGo搜索API（需要安装 ddgs）
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", "")[:500],
                "url": r.get("href", "")
            })
        return json.dumps({"results": formatted}, ensure_ascii=False)
    except ImportError:
        # 降级方案：使用Bing搜索
        return http_search_bing(query, max_results)
    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}"})


def http_search_bing(query: str, max_results: int = 3) -> str:
    """备用搜索：直接请求Bing"""
    url = "https://www.bing.com/search"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, params={"q": query}, timeout=10)
        # 这里需要解析HTML，简化处理
        return json.dumps({"note": "Bing搜索需要解析HTML，建议使用ddgs库", "raw_length": len(response.text)})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ========== 定义工具描述 ==========
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索网络获取最新信息。当用户询问新闻、实时数据、股价、天气等需要最新信息的问题时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "max_results": {"type": "integer", "description": "返回结果数量", "default": 3}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "获取指定网页的完整内容。当用户提供URL并希望了解页面内容时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要获取的网页URL"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "http_request",
            "description": "执行通用的HTTP请求，调用任意API接口。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "请求URL"},
                    "method": {"type": "string", "description": "HTTP方法", "enum": ["GET", "POST"]},
                    "headers": {"type": "object", "description": "请求头"},
                    "body": {"type": "object", "description": "请求体（POST时使用）"}
                },
                "required": ["url", "method"]
            }
        }
    }
]

# 工具名称到函数的映射
TOOL_FUNCTIONS = {
    "web_search": web_search,
    "fetch_webpage": fetch_webpage,
    "http_request": http_request
}


# ========== 智能问答（自动处理HTTP请求） ==========
def ask_with_http_tools(question: str, verbose: bool = True) -> str:
    """
    智能问答，模型可自动调用HTTP工具
    """
    messages = [{"role": "user", "content": question}]

    # 第一轮：模型决定是否调用工具
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.7
    )

    message = response.choices[0].message

    # 如果模型要调用工具
    if message.tool_calls:
        if verbose:
            print(f"🔧 模型决定调用 {len(message.tool_calls)} 个工具...")

        # 添加模型响应到历史
        messages.append(message)

        # 执行每个工具调用
        for tool_call in message.tool_calls:
            func = TOOL_FUNCTIONS.get(tool_call.function.name)
            if func:
                args = json.loads(tool_call.function.arguments)
                if verbose:
                    print(f"   🌐 执行: {tool_call.function.name}({args})")

                # 执行HTTP请求（实际发网络请求）
                result = func(**args)

                # 添加工具结果
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            else:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": f"未知工具: {tool_call.function.name}"})
                })

        # 第二轮：基于工具结果生成最终回答
        if verbose:
            print("   📝 基于网络数据生成回答...")

        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7
        )
        return final_response.choices[0].message.content
    else:
        return message.content


# ========== 使用示例 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 智能问答系统（模型可自动发起HTTP请求）")
    print("=" * 60)

    # 示例1：搜索新闻（模型会自动调用 web_search）
    print("\n【示例1】搜索实时新闻")
    print("-" * 40)
    answer = ask_with_http_tools("今天有什么重要的科技新闻？")
    print(f"\n🤖 回答:\n{answer}")

    # 示例2：获取网页内容
    print("\n" + "=" * 60)
    print("\n【示例2】获取网页内容")
    print("-" * 40)
    answer = ask_with_http_tools("请帮我获取 https://example.com 的内容摘要")
    print(f"\n🤖 回答:\n{answer}")