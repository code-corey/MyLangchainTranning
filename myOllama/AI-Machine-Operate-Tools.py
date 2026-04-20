from openai import OpenAI
import os
import shutil
import json
import glob
from pathlib import Path
from datetime import datetime

# 配置
client = OpenAI(
    base_url="http://192.168.13.23:8842/v1",
    api_key="ollama"
)
MODEL_NAME = "Qwen3.5-27B-Q8_0.gguf"

# ========== 安全配置 ==========
# 设置允许操作的根目录（安全沙箱）
ALLOWED_BASE_DIR = os.path.expanduser("~/ollama_workspace")  # 限制在此目录下操作
os.makedirs(ALLOWED_BASE_DIR, exist_ok=True)


def safe_path(filepath: str) -> str:
    """确保路径在允许的根目录内（安全防护）"""
    full_path = os.path.abspath(os.path.join(ALLOWED_BASE_DIR, filepath))
    if not full_path.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
        raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
    return full_path


# ========== 文件操作工具函数 ==========

def read_file(filepath: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容
    """
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        with open(full_path, 'r', encoding=encoding) as f:
            content = f.read()

        # 限制返回长度，避免超出上下文
        if len(content) > 10000:
            content = content[:10000] + "\n... (内容过长，已截断)"

        return json.dumps({
            "success": True,
            "path": filepath,
            "content": content,
            "size": len(content)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def write_file(filepath: str, content: str, encoding: str = "utf-8") -> str:
    """
    写入文件（覆盖模式）
    """
    try:
        full_path = safe_path(filepath)

        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "path": filepath,
            "action": "written",
            "bytes": len(content.encode(encoding))
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def append_to_file(filepath: str, content: str, encoding: str = "utf-8") -> str:
    """
    追加内容到文件末尾
    """
    try:
        full_path = safe_path(filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'a', encoding=encoding) as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "path": filepath,
            "action": "appended"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """
    列出目录内容
    """
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
                "modified": datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M:%S")
            }
            items.append(item_info)

        # 排序：目录在前，文件在后
        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))

        return json.dumps({
            "success": True,
            "path": path,
            "items": items,
            "count": len(items)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def delete_file(filepath: str) -> str:
    """
    删除文件
    """
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            action = "deleted directory"
        else:
            os.remove(full_path)
            action = "deleted file"

        return json.dumps({
            "success": True,
            "path": filepath,
            "action": action
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def copy_file(source: str, destination: str) -> str:
    """
    复制文件或目录
    """
    try:
        src_path = safe_path(source)
        dst_path = safe_path(destination)

        if not os.path.exists(src_path):
            return json.dumps({"error": f"源文件不存在: {source}"})

        # 确保目标目录存在
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

        return json.dumps({
            "success": True,
            "source": source,
            "destination": destination,
            "action": "copied"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_in_files(query: str, path: str = ".", file_pattern: str = "*") -> str:
    """
    在文件中搜索文本内容
    """
    try:
        full_path = safe_path(path)
        results = []

        # 递归搜索匹配的文件
        pattern = os.path.join(full_path, "**", file_pattern)
        for filepath in glob.glob(pattern, recursive=True):
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                results.append({
                                    "file": os.path.relpath(filepath, full_path),
                                    "line": line_num,
                                    "content": line.strip()[:200]
                                })
                                if len(results) >= 50:  # 限制结果数量
                                    break
                except:
                    continue

            if len(results) >= 50:
                break

        return json.dumps({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_file_info(filepath: str) -> str:
    """
    获取文件详细信息
    """
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        stat = os.stat(full_path)

        return json.dumps({
            "success": True,
            "path": filepath,
            "name": os.path.basename(full_path),
            "type": "directory" if os.path.isdir(full_path) else "file",
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accessed": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ========== 工具定义（告诉模型有哪些功能） ==========
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容。当用户想查看文件内容时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径（相对于工作目录）"},
                    "encoding": {"type": "string", "description": "文件编码，默认utf-8"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件（会覆盖原有内容）。当用户需要创建新文件或覆盖文件时使用。",
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
            "name": "append_to_file",
            "description": "追加内容到文件末尾。当用户想在文件末尾添加内容时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要追加的内容"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "列出目录中的文件和子目录。当用户想查看文件夹内容时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径，默认为当前目录"},
                    "show_hidden": {"type": "boolean", "description": "是否显示隐藏文件"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除文件或目录。当用户需要删除文件时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "要删除的文件或目录路径"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "copy_file",
            "description": "复制文件或目录。当用户需要复制文件时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "源文件路径"},
                    "destination": {"type": "string", "description": "目标路径"}
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_files",
            "description": "在文件中搜索文本内容。当用户需要在文件中查找特定内容时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "path": {"type": "string", "description": "搜索目录"},
                    "file_pattern": {"type": "string", "description": "文件匹配模式，如*.txt"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_info",
            "description": "获取文件的详细信息（大小、时间等）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"}
                },
                "required": ["filepath"]
            }
        }
    }
]

# 工具函数映射
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "append_to_file": append_to_file,
    "list_directory": list_directory,
    "delete_file": delete_file,
    "copy_file": copy_file,
    "search_in_files": search_in_files,
    "get_file_info": get_file_info
}


# ========== 主问答函数 ==========
def ask_with_file_ops(question: str, verbose: bool = True) -> str:
    """
    支持文件操作的智能问答
    """
    messages = [
        {
            "role": "system",
            "content": f"""你是一个文件管理助手。你可以操作文件来完成用户的任务。

【重要规则】
1. 所有文件操作都在 {ALLOWED_BASE_DIR} 目录下进行
2. 使用绝对路径时，会自动转换为相对于工作目录的路径
3. 操作前先确认文件是否存在
4. 删除文件前要确认
5. 写入文件时确保目录存在

【可用操作】
- 读取文件：read_file
- 写入文件：write_file  
- 追加内容：append_to_file
- 列出目录：list_directory
- 删除文件：delete_file
- 复制文件：copy_file
- 搜索内容：search_in_files
- 查看信息：get_file_info

请根据用户需求，选择合适的工具完成任务。"""
        },
        {"role": "user", "content": question}
    ]

    # 模型决定调用哪些工具
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.3
    )

    message = response.choices[0].message

    if message.tool_calls:
        if verbose:
            print(f"🔧 模型决定执行 {len(message.tool_calls)} 个文件操作...")

        messages.append(message)

        for tool_call in message.tool_calls:
            func = TOOL_FUNCTIONS.get(tool_call.function.name)
            if func:
                args = json.loads(tool_call.function.arguments)
                if verbose:
                    print(f"   📁 {tool_call.function.name}({args})")

                result = func(**args)
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

        # 生成最终回答
        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5
        )
        return final_response.choices[0].message.content
    else:
        return message.content


# ========== 使用示例 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 文件操作助手启动")
    print(f"📁 工作目录: {ALLOWED_BASE_DIR}")
    print("=" * 60)

    # 示例1：创建并写入文件
    print("\n【示例1】创建文件")
    print("-" * 40)
    result = ask_with_file_ops("创建一个名为 hello.txt 的文件，内容为 'Hello, World!'")
    print(f"结果: {result}")

    # 示例2：读取文件
    print("\n【示例2】读取文件")
    print("-" * 40)
    result = ask_with_file_ops("读取 hello.txt 的内容")
    print(f"结果: {result}")

    # 示例3：列出目录
    print("\n【示例3】列出目录")
    print("-" * 40)
    result = ask_with_file_ops("列出当前目录下的所有文件")
    print(f"结果: {result}")

    # 示例4：搜索文件内容
    print("\n【示例4】搜索内容")
    print("-" * 40)
    result = ask_with_file_ops("在 hello.txt 中搜索 'World'")
    print(f"结果: {result}")

    # 示例5：交互模式
    print("\n" + "=" * 60)
    print("【交互模式】输入指令，模型会帮你操作文件")
    print("提示：输入 'exit' 退出\n")

    while True:
        user_input = input("👤 你: ").strip()
        if user_input.lower() == 'exit':
            print("👋 再见！")
            break
        if not user_input:
            continue

        print("🤖 思考中...")
        result = ask_with_file_ops(user_input)
        print(f"🤖 结果:\n{result}\n")