from openai import OpenAI
import os
import shutil
import json
import subprocess
import tempfile
import sys
from pathlib import Path
from datetime import datetime
import re

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"

# ========== 安全配置 ==========
# 设置允许操作的根目录
ALLOWED_BASE_DIR = os.path.expanduser("~/ollama_workspace")
os.makedirs(ALLOWED_BASE_DIR, exist_ok=True)

# 允许执行的解释器
ALLOWED_INTERPRETERS = {
    'python': sys.executable,  # 当前Python解释器
    'python3': 'python3',
    'bash': '/bin/bash',
    'sh': '/bin/sh',
    'node': 'node',  # 如果安装了Node.js
}


def safe_path(filepath: str) -> str:
    """确保路径在允许的根目录内（安全防护）"""
    # 如果是绝对路径，确保在工作目录内
    if os.path.isabs(filepath):
        if not filepath.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
            raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
        return filepath

    # 相对路径，拼接到工作目录
    full_path = os.path.abspath(os.path.join(ALLOWED_BASE_DIR, filepath))
    if not full_path.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
        raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
    return full_path


# ========== 文件操作工具函数 ==========

def read_file(filepath: str, encoding: str = "utf-8") -> str:
    """读取文件内容"""
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        with open(full_path, 'r', encoding=encoding) as f:
            content = f.read()

        # 限制返回长度
        if len(content) > 50000:
            content = content[:50000] + "\n... (内容过长，已截断)"

        return json.dumps({
            "success": True,
            "path": filepath,
            "content": content,
            "size": len(content)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def write_file(filepath: str, content: str, encoding: str = "utf-8") -> str:
    """写入文件（覆盖模式）"""
    try:
        full_path = safe_path(filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "path": filepath,
            "action": "written"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """列出目录内容"""
    try:
        full_path = safe_path(path)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"目录不存在: {path}"})

        items = []
        for item in os.listdir(full_path):
            if not show_hidden and item.startswith('.'):
                continue

            item_path = os.path.join(full_path, item)
            item_info = {
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                "executable": os.access(item_path, os.X_OK) if os.path.isfile(item_path) else False
            }
            items.append(item_info)

        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))

        return json.dumps({
            "success": True,
            "path": path,
            "items": items,
            "count": len(items)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ========== 新增：执行文件功能 ==========

def execute_file(filepath: str, args: list = None, timeout: int = 30) -> str:
    """
    执行文件（Python脚本、Shell脚本等）

    Args:
        filepath: 文件路径
        args: 命令行参数列表
        timeout: 超时时间（秒）
    """
    try:
        full_path = safe_path(filepath)

        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        # 根据扩展名判断如何执行
        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.py':
            interpreter = ALLOWED_INTERPRETERS.get('python', sys.executable)
            cmd = [interpreter, full_path]
        elif ext in ['.sh', '.bash']:
            interpreter = ALLOWED_INTERPRETERS.get('bash', '/bin/bash')
            cmd = [interpreter, full_path]
        elif ext == '.js':
            if 'node' not in ALLOWED_INTERPRETERS:
                return json.dumps({"error": "未安装 Node.js，无法执行 .js 文件"})
            cmd = [ALLOWED_INTERPRETERS['node'], full_path]
        else:
            # 尝试作为可执行文件直接运行（Linux/Mac）
            if os.access(full_path, os.X_OK):
                cmd = [full_path]
            else:
                return json.dumps({"error": f"不支持的文件类型: {ext}，且文件不可执行"})

        # 添加参数
        if args:
            cmd.extend(args)

        # 执行文件
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(full_path)  # 在文件所在目录执行
        )

        return json.dumps({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "executed": filepath
        }, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"执行超时（{timeout}秒）"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_python_code(code: str, timeout: int = 30) -> str:
    """
    直接执行 Python 代码字符串（不创建文件）
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=ALLOWED_BASE_DIR) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

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


def make_executable(filepath: str) -> str:
    """
    给文件添加可执行权限（Linux/Mac）
    """
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        # 添加执行权限
        os.chmod(full_path, os.stat(full_path).st_mode | 0o111)

        return json.dumps({
            "success": True,
            "path": filepath,
            "action": "made executable"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def install_package(package_name: str) -> str:
    """
    安装 Python 包（用于执行脚本前安装依赖）
    """
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


# ========== 工具定义 ==========
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件（会覆盖原有内容）",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要写入的内容"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "列出目录中的文件和子目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径，默认为当前目录"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_file",
            "description": "执行文件（Python脚本、Shell脚本等）。当用户需要运行脚本时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "要执行的文件路径"},
                    "args": {"type": "array", "items": {"type": "string"}, "description": "命令行参数"},
                    "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 30}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python_code",
            "description": "直接执行 Python 代码字符串（不保存文件）。适合快速测试代码片段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "要执行的 Python 代码"},
                    "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 30}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_executable",
            "description": "给文件添加可执行权限（Linux/Mac）",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "install_package",
            "description": "安装 Python 包。当执行脚本缺少依赖时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_name": {"type": "string", "description": "要安装的包名"}
                },
                "required": ["package_name"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "execute_file": execute_file,
    "execute_python_code": execute_python_code,
    "make_executable": make_executable,
    "install_package": install_package
}


# ========== 主问答函数 ==========
def ask_with_execution(question: str, verbose: bool = True) -> str:
    """
    支持文件执行和代码运行的智能问答
    """
    messages = [
        {
            "role": "system",
            "content": f"""你是一个强大的 AI 助手，可以创建、读取、执行文件。

【工作目录】
{ALLOWED_BASE_DIR}

【可用操作】
- 读写文件：write_file, read_file
- 执行文件：execute_file（运行 .py, .sh 等文件）
- 执行代码：execute_python_code（直接运行 Python 代码）
- 安装依赖：install_package（安装 pip 包）
- 设置权限：make_executable（给文件加执行权限）
- 查看目录：list_directory

【工作流程建议】
1. 先创建/写入代码文件
2. 如果需要依赖，先 install_package
3. 执行文件
4. 如果出错，分析错误并修正

【安全规则】
- 所有操作限制在工作目录内
- 不要执行危险的系统命令
- 执行前确认文件内容正确

请根据用户需求完成任务。"""
        },
        {"role": "user", "content": question}
    ]

    # 多轮工具调用（最多5轮）
    max_iterations = 500
    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3
        )

        message = response.choices[0].message

        # 如果没有工具调用，返回结果
        if not message.tool_calls:
            return message.content

        if verbose:
            print(f"\n🔄 第 {iteration + 1} 轮工具调用")

        messages.append(message)

        # 执行所有工具调用
        for tool_call in message.tool_calls:
            func = TOOL_FUNCTIONS.get(tool_call.function.name)
            if func:
                args = json.loads(tool_call.function.arguments)
                if verbose:
                    print(f"   🔧 {tool_call.function.name}({json.dumps(args, ensure_ascii=False)[:100]})")

                result = func(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

                if verbose and "error" not in result:
                    # 显示执行结果摘要
                    try:
                        data = json.loads(result)
                        if data.get("success"):
                            if "stdout" in data and data["stdout"]:
                                print(f"   📤 输出: {data['stdout'][:200]}")
                    except:
                        pass
            else:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": f"未知工具: {tool_call.function.name}"})
                })

    # 超过最大轮次
    final_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.5
    )
    return final_response.choices[0].message.content


# ========== 交互式使用 ==========
if __name__ == "__main__":
    print("=" * 70)
    print("🤖 AI 编程助手（支持创建、执行、调试代码）")
    print(f"📁 工作目录: {ALLOWED_BASE_DIR}")
    print("=" * 70)
    print("\n💡 示例命令：")
    print("  • '创建一个Python脚本，打印1到10'")
    print("  • '写个函数计算斐波那契数列，并执行'")
    print("  • '帮我写个爬虫抓取网页标题'")
    print("  • '列出当前目录所有文件'")
    print("=" * 70)

    while True:
        user_input = input("\n👤 你: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("👋 再见！")
            break
        if not user_input:
            continue

        print("🤖 思考中...")
        result = ask_with_execution(user_input, verbose=True)
        print(f"\n✅ 结果:\n{result}")