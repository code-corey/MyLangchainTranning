import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from mcp.types import ServerCapabilities  # 需要添加这个导入

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# ========== 配置 ==========
ALLOWED_BASE_DIR = os.path.expanduser("~/ollama_workspace")
os.makedirs(ALLOWED_BASE_DIR, exist_ok=True)

ALLOWED_INTERPRETERS = {
    'python': sys.executable,
    'python3': 'python3',
    'bash': '/bin/bash',
    'sh': '/bin/sh',
    'node': 'node',
}


# ========== 安全函数 ==========
def safe_path(filepath: str) -> str:
    if os.path.isabs(filepath):
        if not filepath.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
            raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
        return filepath
    full_path = os.path.abspath(os.path.join(ALLOWED_BASE_DIR, filepath))
    if not full_path.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
        raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
    return full_path


# ========== 工具函数 ==========
async def read_file(filepath: str, encoding: str = "utf-8") -> str:
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})
        with open(full_path, 'r', encoding=encoding) as f:
            content = f.read()
        if len(content) > 50000:
            content = content[:50000] + "\n... (内容过长，已截断)"
        return json.dumps({"success": True, "path": filepath, "content": content})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def write_file(filepath: str, content: str, encoding: str = "utf-8") -> str:
    try:
        full_path = safe_path(filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)
        return json.dumps({"success": True, "path": filepath, "action": "written"})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    try:
        full_path = safe_path(path)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"目录不存在: {path}"})
        items = []
        for item in os.listdir(full_path):
            if not show_hidden and item.startswith('.'):
                continue
            item_path = os.path.join(full_path, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
            })
        return json.dumps({"success": True, "path": path, "items": items, "count": len(items)})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def execute_file(filepath: str, args: list = None, timeout: int = 30) -> str:
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.py':
            cmd = [ALLOWED_INTERPRETERS.get('python', sys.executable), full_path]
        elif ext in ['.sh', '.bash']:
            cmd = [ALLOWED_INTERPRETERS.get('bash', '/bin/bash'), full_path]
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
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"执行超时（{timeout}秒）"})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def execute_python_code(code: str, timeout: int = 30) -> str:
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=ALLOWED_BASE_DIR) as f:
            f.write(code)
            temp_file = f.name
        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=timeout)
        os.unlink(temp_file)
        return json.dumps({"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr})
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"执行超时（{timeout}秒）"})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def delete_file(filepath: str) -> str:
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return json.dumps({"success": True, "path": filepath, "action": "deleted"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ========== 创建 MCP Server ==========
app = Server("file-code-executor")


# 注册工具列表
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_file",
            description="读取文件内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"},
                    "encoding": {"type": "string", "description": "编码，默认utf-8"}
                },
                "required": ["filepath"]
            }
        ),
        types.Tool(
            name="write_file",
            description="写入文件（会覆盖原有内容）",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要写入的内容"}
                },
                "required": ["filepath", "content"]
            }
        ),
        types.Tool(
            name="list_directory",
            description="列出目录中的文件和子目录",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径，默认为当前目录"},
                    "show_hidden": {"type": "boolean", "description": "是否显示隐藏文件"}
                }
            }
        ),
        types.Tool(
            name="execute_file",
            description="执行文件（Python脚本、Shell脚本等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "要执行的文件路径"},
                    "args": {"type": "array", "items": {"type": "string"}, "description": "命令行参数"},
                    "timeout": {"type": "integer", "description": "超时时间（秒）"}
                },
                "required": ["filepath"]
            }
        ),
        types.Tool(
            name="execute_python_code",
            description="直接执行 Python 代码字符串",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "要执行的 Python 代码"},
                    "timeout": {"type": "integer", "description": "超时时间（秒）"}
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="delete_file",
            description="删除文件或目录",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "要删除的文件或目录路径"}
                },
                "required": ["filepath"]
            }
        )
    ]


# 注册工具调用处理
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    args = arguments if arguments else {}

    if name == "read_file":
        result = await read_file(args.get("filepath", ""), args.get("encoding", "utf-8"))
    elif name == "write_file":
        result = await write_file(args.get("filepath", ""), args.get("content", ""), args.get("encoding", "utf-8"))
    elif name == "list_directory":
        result = await list_directory(args.get("path", "."), args.get("show_hidden", False))
    elif name == "execute_file":
        result = await execute_file(args.get("filepath", ""), args.get("args"), args.get("timeout", 30))
    elif name == "execute_python_code":
        result = await execute_python_code(args.get("code", ""), args.get("timeout", 30))
    elif name == "delete_file":
        result = await delete_file(args.get("filepath", ""))
    else:
        result = json.dumps({"error": f"未知工具: {name}"})

    return [types.TextContent(type="text", text=result)]


# ========== 启动服务器 ==========
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="file-code-executor",
                server_version="1.0.0",
                capabilities=ServerCapabilities()  # 必需参数
            )
        )


if __name__ == "__main__":
    asyncio.run(main())