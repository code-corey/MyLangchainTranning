import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.tools import tool
import operator
import json

load_dotenv()


# ==================== 1. 定义工具 ====================
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 模拟天气数据（实际可调用真实 API）
    weather_data = {
        "北京": "晴天，25°C，空气质量良好",
        "上海": "多云，22°C，可能有小雨",
        "深圳": "晴天，28°C，炎热",
    }
    return weather_data.get(city, f"抱歉，没有找到{city}的天气信息")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except:
        return f"无法计算: {expression}"


# 工具列表
tools = [get_weather, calculate]

# ==================== 2. 配置 LLM ====================
llm = ChatOpenAI(
    model="qwen-turbo",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
).bind_tools(tools)


# ==================== 3. 定义状态 ====================
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# ==================== 4. 定义节点 ====================
def call_model(state: AgentState) -> dict:
    """LLM 节点：决定是否需要调用工具"""
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", END]:
    """条件判断：是否需要调用工具"""
    last_message = state["messages"][-1]

    # 如果 LLM 要求调用工具，就去 tools 节点
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # 否则结束
    return END


# ==================== 5. 构建图 ====================
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("llm", call_model)
workflow.add_node("tools", ToolNode(tools))

# 设置入口
workflow.set_entry_point("llm")

# 添加边
workflow.add_conditional_edges("llm", should_continue)
workflow.add_edge("tools", "llm")  # 工具执行完后回到 LLM

# 编译
app = workflow.compile()

# ==================== 6. 运行 ====================
if __name__ == "__main__":
    print("🤖 LangGraph Agent with Tools Demo")
    print("=" * 60)

    # 测试用例
    test_questions = [
        "北京天气怎么样？",
        "帮我计算 25 * 4 + 10",
        "上海和深圳哪个天气更好？"
    ]

    for question in test_questions:
        print(f"\n👤 用户: {question}")

        result = app.invoke({
            "messages": [HumanMessage(content=question)]
        })

        answer = result["messages"][-1].content
        print(f"🤖 AI: {answer}")
        print("-" * 60)