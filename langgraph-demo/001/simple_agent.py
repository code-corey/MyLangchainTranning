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

"""

这行代码的意思是：messages 是一个消息列表，每次更新时把新消息追加到后面，而不是替换整个列表

Annotated[Sequence[BaseMessage], operator.add]
    ↑           ↑                    ↑
    │           │                    └─ 第2个参数：如何合并
    │           └────────────────────── 第1个参数：数据类型
    └────────────────────────────────── 语法标记
"""

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

    # 取出对话历史
    messages = state["messages"]
    # 调用AI，取得回复
    response = llm.invoke(messages)
    # 返回新消息
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """判断是否需要继续（本 demo 直接结束）"""
    # 简单版本：总是结束
    return "end"


# ==================== 4. 构建图 ====================
# 创建图
# 直译：创建一个状态图，这个图使用 AgentState 作为状态结构
"""
LangGraph 提供的图构建器类
用来定义 AI Agent 的工作流程
决定：有哪些步骤、步骤之间的顺序、如何传递数据


类比1：工厂流水线
# AgentState 是产品的设计图纸
class AgentState(TypedDict):
    messages: list  # 产品要有消息列表

# 创建生产线，告诉生产线要按照这个图纸生产
workflow = StateGraph(AgentState)  # 创建一条按照图纸运作的流水线


类比2：快递系统
# AgentState 是快递单格式
class AgentState(TypedDict):
    messages: list  # 快递单必须有"物流信息"字段

# 建立快递系统，所有包裹必须使用这个格式的快递单
workflow = StateGraph(AgentState)  # 创建按照这个快递单格式运行的系统



类比3：表单填写
# AgentState 是表单模板
class AgentState(TypedDict):
    messages: list  # 表单有一个"聊天记录"栏目

# 创建流程，所有环节都要传递这个表单
workflow = StateGraph(AgentState)  # 建立传递这个表单的工作流程
"""
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("llm", call_model)

# 设置入口
workflow.set_entry_point("llm")

# 添加边：llm → END
workflow.add_edge("llm", END)

# 编译
app = workflow.compile()


"""
一、核心理解：就像画流程图
workflow = StateGraph(AgentState)     # 1. 拿出一张白纸
workflow.add_node("llm", call_model)  # 2. 画一个步骤（节点）
workflow.set_entry_point("llm")       # 3. 标记起点
workflow.add_edge("llm", END)         # 4. 画箭头（从步骤指向结束）
app = workflow.compile()              # 5. 把图画变成可执行程序



    ┌─────────────────┐
    │   START (入口)   │
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │  节点: "llm"     │
    │  执行: call_model│
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │      END        │
    └─────────────────┘
    
    
    
    
# 这5行代码 = 做一个简单的流水线
workflow = StateGraph(AgentState)     # 拿流水线图纸
workflow.add_node("llm", call_model)  # 放一个工人（做AI回复）
workflow.set_entry_point("llm")       # 告诉工人：从这里开始
workflow.add_edge("llm", END)         # 做完就去终点
app = workflow.compile()              # 启动流水线
"""

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