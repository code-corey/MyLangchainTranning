from openai import OpenAI
import subprocess
import tempfile
import os
import json
import re

client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"


# ========== 工具函数 ==========
def execute_python_code(code: str) -> str:
    """执行Python代码并返回结果"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        os.unlink(temp_file)

        return json.dumps({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def generate_code_snippet(requirement: str) -> str:
    """根据需求生成代码（不执行）"""
    # 这个函数让模型自己调用，用于生成复杂代码
    return f"已根据需求生成代码：{requirement[:100]}..."


# ========== 定义工具 ==========
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_python_code",
            "description": "执行Python代码并返回结果。当用户需要计算、数据处理、或验证代码逻辑时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的完整Python代码"
                    }
                },
                "required": ["code"]
            }
        }
    }
]


def ask_with_code_execution(question: str) -> str:
    """智能问答，模型可主动执行代码"""

    messages = [
        {
            "role": "system",
            "content": """你是一个编程助手。当用户需要计算、数据分析、或任何可以通过写代码解决的问题时，
            请使用 execute_python_code 工具来执行代码。代码要完整、有注释、包含必要的异常处理。"""
        },
        {"role": "user", "content": question}
    ]

    # 第一轮：模型决定是否执行代码
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        print("🔧 模型决定写代码来解决问题...")

        messages.append(message)

        for tool_call in message.tool_calls:
            if tool_call.function.name == "execute_python_code":
                args = json.loads(tool_call.function.arguments)
                code = args.get("code")

                print(f"📝 生成的代码：\n{code}\n")
                print("🚀 执行中...")

                result = execute_python_code(code)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        # 第二轮：基于执行结果回答
        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        return message.content


# 使用示例
if __name__ == "__main__":
    # 模型会自己写代码计算
    answer = ask_with_code_execution("计算斐波那契数列的前20项")
    print(f"🤖 回答：\n{answer}")