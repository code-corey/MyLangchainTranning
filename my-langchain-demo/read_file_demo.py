from langchain.agents import create_tool_calling_agent
from langchain_core.tools import tool

@tool
def read_file(path: str) -> str:
    """读取文件"""
    with open(path, 'r') as f:
        return f.read()

tools = [read_file]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# 同一进程内执行，可以访问所有文件
result = executor.invoke({"input": "读取 config.json"})