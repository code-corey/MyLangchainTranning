import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

# 加载环境变量
load_dotenv()


# ==================== 1. 定义状态 ====================
class AgentState(TypedDict):
    """Agent 的状态"""
    messages: Annotated[Sequence[BaseMessage], operator.add]


# ==================== 2. 配置阿里云 DashScope ====================
# 阿里云 DashScope 兼容 OpenAI API
llm = ChatOpenAI(
    model="qwen3.5-flash",  # 可选: qwen-turbo, qwen-plus, qwen-max
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
)


# ==================== 3. 定义节点函数 ====================
def call_model(state: AgentState) -> dict:
    """调用 LLM 的节点"""
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """判断是否需要继续（本 demo 直接结束）"""
    # 简单版本：总是结束
    return "end"


# ==================== 4. 构建图 ====================
# 创建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("llm", call_model)

# 设置入口
workflow.set_entry_point("llm")

# 添加边：llm → END
workflow.add_edge("llm", END)

# 编译
app = workflow.compile()

# ==================== 5. 运行测试 ====================
if __name__ == "__main__":
    print("🤖 LangGraph 简单 Demo 启动！")
    print("-" * 50)

    # 测试问题
    questions = [
        "你是谁？",
        "用一句话解释什么是 LangGraph",
        "1 + 1 等于几？"
    ]

    for question in questions:
        print(f"\n👤 用户: {question}")

        # 调用 Agent
        result = app.invoke({
            "messages": [HumanMessage(content=question)]
        })

        # 获取最后的回答
        answer = result["messages"][-1].content
        print(f"🤖 AI: {answer}")
        print("-" * 50)