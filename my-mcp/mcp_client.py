#!/usr/bin/env python3
"""
MCP 代码助手客户端
通过 MCP 协议调用服务器执行代码和文件操作
"""
import asyncio
import json
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ========== 配置 ==========
OPENAI_CONFIG = {
    "base_url": "http://192.168.13.23:8842/v1",
    "api_key": "ollama"
}

MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"

# 获取当前脚本所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MCP_SERVER_PATH = os.path.join(CURRENT_DIR, "mcp_server.py")

# MCP 服务器启动命令
MCP_SERVER_COMMAND = [sys.executable, MCP_SERVER_PATH]


class MCPCodeAssistant:
    """MCP 代码助手客户端"""

    def __init__(self, server_command: list, openai_config: dict):
        self.server_command = server_command
        self.openai_config = openai_config
        self.client_context = None  # 存储 stdio_client 上下文
        self.session_context = None  # 存储 session 上下文
        self.session = None
        self.mcp_tools = []

    async def connect(self):
        """连接到 MCP 服务器"""

        # 1、创建服务器参数: 配置如何启动 MCP 服务器子进程
        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:]
        )

        # 正确管理上下文
        # 2、建立 stdio 连接: stdio_client 启动服务器子进程，返回读写流
        self.client_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.client_context.__aenter__()

        # 3、创建客户端会话: ClientSession 管理协议通信
        self.session_context = ClientSession(self.read_stream, self.write_stream)
        self.session = await self.session_context.__aenter__()

        # 4、初始化会话: initialize() 完成握手
        await self.session.initialize()

        # 5、获取工具列表: list_tools() 询问服务器有哪些可用工具
        tools_result = await self.session.list_tools()

        # 6、转换工具格式: 将 MCP 工具格式转换为 OpenAI 函数调用格式
        self.mcp_tools = self._convert_to_openai_tools(tools_result.tools)

        print(f"✅ 已连接 MCP 服务器，加载 {len(self.mcp_tools)} 个工具")
        print(f"📁 工作目录: ~/ollama_workspace")
        return self.mcp_tools

    def _convert_to_openai_tools(self, mcp_tools):
        """将 MCP 工具转换为 OpenAI function 格式"""
        openai_tools = []
        for tool in mcp_tools:
            # 确保参数格式正确
            input_schema = tool.inputSchema if hasattr(tool, 'inputSchema') else {
                "type": "object",
                "properties": {}
            }

            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"调用 {tool.name} 工具",
                    "parameters": input_schema
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用 MCP 工具"""
        try:
            result = await self.session.call_tool(tool_name, arguments)

            # 解析返回结果
            if result.content:
                text_content = []
                for c in result.content:
                    if hasattr(c, 'text'):
                        text_content.append(c.text)
                    elif hasattr(c, 'data'):
                        text_content.append(str(c.data))

                if text_content:
                    # 尝试解析 JSON
                    try:
                        return json.loads(text_content[0])
                    except json.JSONDecodeError:
                        return {"raw_output": text_content[0]}

            return {"success": False, "content": []}
        except Exception as e:
            return {"error": str(e)}

    async def ask(self, question: str, verbose: bool = True, max_iterations: int = 10) -> str:
        """向 AI 提问，自动调用 MCP 工具"""
        openai_client = OpenAI(**self.openai_config)

        messages = [
            {
                "role": "system",
                "content": f"""你是一个强大的 AI 代码助手，可以通过 MCP 协议执行代码和操作文件。

## 工作目录
~/ollama_workspace

## 可用工具
{', '.join([t['function']['name'] for t in self.mcp_tools])}

## 工具说明
- read_file: 读取文件内容
- write_file: 写入/创建文件
- list_directory: 浏览目录
- execute_file: 执行脚本文件（.py, .sh 等）
- execute_python_code: 直接执行 Python 代码片段
- install_package: 安装 Python 包
- make_executable: 添加执行权限
- delete_file: 删除文件
- get_workspace_info: 查看工作区信息

## 工作流程
1. 先创建/写入代码文件
2. 如需依赖，先 install_package
3. 执行文件或代码
4. 分析结果，如有错误则修正

## 安全规则
- 所有操作限制在工作目录内
- 不要执行危险的系统命令

请根据用户需求完成任务。"""
            },
            {"role": "user", "content": question}
        ]

        for iteration in range(max_iterations):
            try:
                response = openai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=self.mcp_tools,
                    tool_choice="auto",
                    temperature=0.3
                )
            except Exception as e:
                return f"调用 AI 模型失败: {e}"

            message = response.choices[0].message

            # 没有工具调用，返回结果
            if not message.tool_calls:
                return message.content or "任务完成"

            if verbose:
                print(f"\n🔄 第 {iteration + 1} 轮工具调用")

            messages.append(message)

            # 执行所有工具调用
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                if verbose:
                    args_str = json.dumps(args, ensure_ascii=False)[:100]
                    print(f"   🔧 {tool_name}({args_str})")

                # 调用 MCP 工具
                result = await self.call_tool(tool_name, args)

                # 显示执行结果摘要
                if verbose and result.get("success"):
                    if "stdout" in result and result["stdout"]:
                        output = result['stdout'][:200]
                        print(f"   📤 输出: {output}")
                    elif "content" in result and result["content"]:
                        content = str(result['content'])[:200]
                        print(f"   📄 内容: {content}")
                    elif result.get("success") and "action" in result:
                        print(f"   ✅ 操作: {result['action']}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

        # 超过最大轮次，获取最终回复
        try:
            final_response = openai_client.chat.completions.create(
                model=self.openai_config.get("model"),
                messages=messages,
                temperature=0.5
            )
            return final_response.choices[0].message.content or "达到最大迭代次数"
        except Exception as e:
            return f"获取最终回复失败: {e}"

    async def close(self):
        """正确关闭连接"""
        try:
            # 先关闭 session
            if self.session_context and self.session:
                try:
                    await self.session_context.__aexit__(None, None, None)
                except Exception as e:
                    print(f"关闭 session 时出错: {e}")

            # 再关闭 client
            if self.client_context:
                try:
                    await self.client_context.__aexit__(None, None, None)
                except Exception as e:
                    print(f"关闭 client 时出错: {e}")

        except Exception as e:
            print(f"关闭连接时出错: {e}")


# ========== 交互式命令行 ==========
async def main():
    """主函数"""
    # 检查服务器文件是否存在
    if not os.path.exists(MCP_SERVER_PATH):
        print(f"❌ 错误: 找不到 MCP 服务器文件: {MCP_SERVER_PATH}")
        print("请确保 mcp_server.py 和 mcp_client.py 在同一个目录下")
        return

    assistant = MCPCodeAssistant(MCP_SERVER_COMMAND, OPENAI_CONFIG)

    try:
        # 连接 MCP 服务器
        await assistant.connect()

        print("=" * 70)
        print("🤖 MCP 代码助手（通过 MCP 协议执行代码）")
        print("=" * 70)
        print("\n💡 示例命令：")
        print("  • '创建一个 Python 脚本，打印 1 到 10'")
        print("  • '写个函数计算斐波那契数列，并执行'")
        print("  • '列出当前目录所有文件'")
        print("  • '安装 requests 包，然后写个爬虫抓取网页'")
        print("=" * 70)

        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 再见！")
                    break
                if not user_input:
                    continue

                print("🤖 思考中...")
                result = await assistant.ask(user_input, verbose=True)
                print(f"\n✅ 结果:\n{result}")
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")

    finally:
        await assistant.close()


if __name__ == "__main__":
    asyncio.run(main())