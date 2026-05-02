# config.py
import os
import sys

# OpenAI 兼容的 API 配置
OPENAI_CONFIG = {
    "base_url": "http://192.168.13.23:8842/v1",
    "api_key": "ollama",
    "model": "Qwen3.5-27B-Q8_0.gguf"
}

# MCP 服务器配置
MCP_SERVER_COMMAND = ["python", "mcp_server.py"]

# 工作目录
WORKSPACE_DIR = os.path.expanduser("~/ollama_workspace")