#!/usr/bin/env python3
"""
LangGraph 版本的代码助手 - 更灵活的工作流控制
"""
import os
import json
import subprocess
import tempfile
import sys
from typing import Optional, TypedDict, Annotated, List, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ========== 安全配置 ==========
ALLOWED_BASE_DIR = os.path.expanduser("~/ollama_workspace")
os.makedirs(ALLOWED_BASE_DIR, exist_ok=True)

ALLOWED_INTERPRETERS = {
    'python': sys.executable,
    'python3': 'python3',
    'bash': '/bin/bash',
    'sh': '/bin/sh',
    'node': 'node',
}


def safe_path(filepath: str) -> str:
    """确保路径安全"""
    if os.path.isabs(filepath):
        if not filepath.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
            raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
        return filepath
    full_path = os.path.abspath(os.path.join(ALLOWED_BASE_DIR, filepath))
    if not full_path.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
        raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
    return full_path


# ========== 工具定义 ==========

@tool
def read_file(filepath: str) -> str:
    """读取文件内容。filepath: 文件路径（相对于工作目录或绝对路径）"""
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if len(content) > 50000:
            content = content[:50000] + "\n... (内容过长，已截断)"

        return json.dumps({"success": True, "content": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def write_file(filepath: str, content: str) -> str:
    """写入文件（会覆盖原有内容）。filepath: 文件路径，content: 要写入的内容"""
    try:
        full_path = safe_path(filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({"success": True, "path": filepath, "action": "written"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def list_directory(path: str = ".") -> str:
    """列出目录内容。path: 目录路径，默认为当前目录"""
    try:
        full_path = safe_path(path)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"目录不存在: {path}"})

        items = []
        for item in os.listdir(full_path):
            if item.startswith('.'):
                continue
            item_path = os.path.join(full_path, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
            })

        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))

        return json.dumps({"success": True, "items": items, "count": len(items)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def execute_file(filepath: str, args: Optional[list] = None, timeout: int = 30) -> str:
    """执行文件（Python脚本、Shell脚本等）。filepath: 文件路径，args: 命令行参数列表，timeout: 超时时间"""
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.py':
            cmd = [ALLOWED_INTERPRETERS['python'], full_path]
        elif ext in ['.sh', '.bash']:
            cmd = [ALLOWED_INTERPRETERS['bash'], full_path]
        elif ext == '.js':
            if 'node' not in ALLOWED_INTERPRETERS:
                return json.dumps({"error": "未安装 Node.js"})
            cmd = [ALLOWED_INTERPRETERS['node'], full_path]
        else:
            if os.access(full_path, os.X_OK):
                cmd = [full_path]
            else:
                return json.dumps({"error": f"不支持的文件类型: {ext}"})

        if args:
            cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=os.path.dirname(full_path))

        return json.dumps({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"执行超时（{timeout}秒）"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def execute_python_code(code: str, timeout: int = 30) -> str:
    """直接执行 Python 代码字符串。code: Python代码，timeout: 超时时间"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=ALLOWED_BASE_DIR) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=timeout)
        os.unlink(temp_file)

        return json.dumps({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"执行超时（{timeout}秒）"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def install_package(package_name: str) -> str:
    """安装 Python 包。package_name: 要安装的包名"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        return json.dumps({
            "success": result.returncode == 0,
            "package": package_name,
            "output": result.stdout if result.returncode == 0 else result.stderr
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_workspace_info() -> str:
    """获取工作区信息，包括当前目录、可用空间等"""
    try:
        info = {
            "workspace": ALLOWED_BASE_DIR,
            "exists": os.path.exists(ALLOWED_BASE_DIR),
            "writable": os.access(ALLOWED_BASE_DIR, os.W_OK)
        }
        return json.dumps(info, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ========== 定义状态 ==========

class AgentState(MessagesState):
    """Agent 状态定义"""
    # 继承 MessagesState，自动包含 messages
    next_step: str  # 下一步要执行的操作
    iteration_count: int  # 迭代次数
    max_iterations: int  # 最大迭代次数


# ========== 创建 LangGraph ==========

def create_code_assistant_graph():
    """创建代码助手的 LangGraph"""

    # 初始化 LLM
    llm = ChatOpenAI(
        base_url="http://192.168.13.23:8842/v1",
        api_key="ollama",
        model="Qwen3.5-27B-Q8_0.gguf",
        temperature=0.3,
    )

    # 工具列表
    tools = [
        read_file,
        write_file,
        list_directory,
        execute_file,
        execute_python_code,
        install_package,
        get_workspace_info,
    ]

    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)

    # 创建工具节点
    tool_node = ToolNode(tools)

    # 系统提示词
    system_prompt = f"""你是一个强大的 AI 助手，可以创建、读取、执行文件。

【工作目录】
{ALLOWED_BASE_DIR}

【可用工具】
- read_file: 读取文件内容
- write_file: 写入/创建文件
- list_directory: 浏览目录
- execute_file: 执行脚本文件（.py, .sh 等）
- execute_python_code: 直接执行 Python 代码片段
- install_package: 安装 Python 包
- get_workspace_info: 查看工作区信息

【工作流程建议】
1. 先创建/写入代码文件（write_file）
2. 如果需要依赖，先 install_package
3. 执行文件（execute_file）或直接执行代码（execute_python_code）
4. 如果出错，分析错误并修正

【安全规则】
- 所有操作限制在工作目录内
- 不要执行危险的系统命令

请根据用户需求完成任务。"""

    # 定义 Agent 节点函数
    def agent_node(state: AgentState):
        """Agent 节点：决定下一步做什么"""
        messages = state["messages"]
        iteration = state.get("iteration_count", 0)

        # 检查是否超过最大迭代次数
        if iteration >= state.get("max_iterations", 20):
            return {
                "messages": messages + [AIMessage(content="已达到最大迭代次数，停止执行。")],
                "next_step": "end"
            }

        # 添加系统提示（只在第一条消息时添加）
        if not any(isinstance(m, AIMessage) and m.content == system_prompt for m in messages):
            messages = [HumanMessage(content=system_prompt)] + messages

        # 调用 LLM
        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response],
            "iteration_count": iteration + 1
        }

    # 定义路由函数
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """判断是否继续执行工具"""
        messages = state["messages"]
        last_message = messages[-1]

        # 如果 LLM 调用了工具，继续到工具节点
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # 否则结束
        return "end"

    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # 设置入口点
    workflow.set_entry_point("agent")

    # 添加条件边
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # 添加工具到 agent 的边
    workflow.add_edge("tools", "agent")

    # 配置检查点（用于保存状态）
    memory = MemorySaver()

    # 编译图
    app = workflow.compile(checkpointer=memory)

    return app


# ========== 交互式使用 ==========

def main():
    print("=" * 70)
    print("🤖 LangGraph AI 编程助手（图结构工作流）")
    print(f"📁 工作目录: {ALLOWED_BASE_DIR}")
    print("=" * 70)
    print("\n💡 示例命令：")
    print("  • '创建一个Python脚本，打印1到10'")
    print("  • '写个函数计算斐波那契数列，并执行'")
    print("  • '帮我写个爬虫抓取网页标题'")
    print("  • '列出当前目录所有文件'")
    print("=" * 70)
    print("\n🔄 LangGraph 特性：")
    print("  • 图结构工作流，更灵活")
    print("  • 自动保存对话状态")
    print("  • 支持复杂分支逻辑")
    print("=" * 70)

    # 创建图
    graph = create_code_assistant_graph()

    # 会话配置
    session_id = "user_session_1"
    config = {"configurable": {"thread_id": session_id}}

    while True:
        user_input = input("\n👤 你: ").strip()
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("👋 再见！")
            break
        if not user_input:
            continue

        print("🤖 思考中...")
        try:
            # 调用图
            events = graph.stream(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "iteration_count": 0,
                    "max_iterations": 20
                },
                config=config,
                stream_mode="values"
            )

            # 处理流式输出
            final_response = None
            for event in events:
                if "messages" in event:
                    messages = event["messages"]
                    if messages:
                        last_msg = messages[-1]
                        if isinstance(last_msg, AIMessage) and last_msg.content:
                            final_response = last_msg.content
                            # 实时打印思考过程
                            if last_msg.tool_calls:
                                print(f"\n   🔧 调用工具: {[tc['name'] for tc in last_msg.tool_calls]}")

            if final_response:
                print(f"\n✅ 结果:\n{final_response}")
            else:
                print("\n⚠️ 没有收到有效响应")

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()


# ========== 高级功能：自定义工作流 ==========

def create_advanced_workflow():
    """
    创建更复杂的工作流示例
    包含：代码生成 -> 测试 -> 执行 -> 修复 的完整循环
    """

    class AdvancedState(TypedDict):
        messages: List[BaseMessage]
        code_generated: bool
        test_passed: bool
        error_count: int
        current_code: str

    # 这里可以定义更复杂的图结构
    # 例如：
    # generate_code -> test_code -> {pass: execute, fail: fix_code} -> generate_code
    pass


if __name__ == "__main__":
    main()