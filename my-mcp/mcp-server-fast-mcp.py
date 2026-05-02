# fastmcp_http_server.py
import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.routing import Mount
import uvicorn

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


def safe_path(filepath: str) -> str:
    if os.path.isabs(filepath):
        if not filepath.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
            raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
        return filepath

    full_path = os.path.abspath(os.path.join(ALLOWED_BASE_DIR, filepath))
    if not full_path.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
        raise PermissionError(f"禁止访问根目录外的文件: {filepath}")
    return full_path


# ========== 创建 FastMCP 实例 ==========
mcp = FastMCP("file-code-executor")


# ========== 工具函数 ==========
@mcp.tool()
def read_file(filepath: str, encoding: str = "utf-8") -> str:
    """读取文件内容"""
    try:
        full_path = safe_path(filepath)
        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        with open(full_path, 'r', encoding=encoding) as f:
            content = f.read()

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


@mcp.tool()
def write_file(filepath: str, content: str, encoding: str = "utf-8") -> str:
    """写入文件"""
    try:
        full_path = safe_path(filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "path": filepath,
            "action": "written",
            "size": len(content)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def append_to_file(filepath: str, content: str, encoding: str = "utf-8") -> str:
    """追加内容到文件"""
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


@mcp.tool()
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
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                "executable": os.access(item_path, os.X_OK) if os.path.isfile(item_path) else False,
                "modified": datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M:%S")
            })

        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))

        return json.dumps({
            "success": True,
            "path": path,
            "items": items,
            "count": len(items)
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def execute_file(filepath: str, args: Optional[List[str]] = None, timeout: int = 30) -> str:
    """执行文件"""
    try:
        full_path = safe_path(filepath)

        if not os.path.exists(full_path):
            return json.dumps({"error": f"文件不存在: {filepath}"})

        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.py':
            interpreter = ALLOWED_INTERPRETERS.get('python', sys.executable)
            cmd = [interpreter, full_path]
        elif ext in ['.sh', '.bash']:
            interpreter = ALLOWED_INTERPRETERS.get('bash', '/bin/bash')
            cmd = [interpreter, full_path]
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

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(full_path)
        )

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


@mcp.tool()
def execute_python_code(code: str, timeout: int = 30) -> str:
    """执行 Python 代码"""
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


@mcp.tool()
def delete_file(filepath: str) -> str:
    """删除文件或目录"""
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


@mcp.tool()
def copy_file(source: str, destination: str) -> str:
    """复制文件或目录"""
    try:
        src_path = safe_path(source)
        dst_path = safe_path(destination)

        if not os.path.exists(src_path):
            return json.dumps({"error": f"源文件不存在: {source}"})

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


@mcp.tool()
def get_file_info(filepath: str) -> str:
    """获取文件详细信息"""
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


@mcp.tool()
def search_in_files(query: str, path: str = ".", file_pattern: str = "*") -> str:
    """在文件中搜索内容"""
    try:
        full_path = safe_path(path)
        results = []

        for filepath in Path(full_path).rglob(file_pattern):
            if filepath.is_file():
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                results.append({
                                    "file": str(filepath.relative_to(full_path)),
                                    "line": line_num,
                                    "content": line.strip()[:200]
                                })
                                if len(results) >= 50:
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="端口")

    args = parser.parse_args()

    print(f"🚀 启动 FastMCP SSE Server")
    print(f"📁 工作目录: {ALLOWED_BASE_DIR}")

    # 只保留基础参数，确保能正常启动
    mcp.run(
        transport="sse",
        host=args.host,
        port=args.port
    )