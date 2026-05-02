import asyncio
from mcp import ClientSession, StdioServerParameters


async def query_context7_simple(library: str, query: str):
    """使用更简洁的方式调用 MCP"""

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp@latest"]
    )

    # 使用 create_session 上下文管理器（如果可用）
    try:
        from mcp.client.session import create_session
        async with create_session(server_params) as session:
            await session.initialize()

            # 调用工具
            result = await session.call_tool(
                "resolve-library",
                arguments={"libraryName": library}
            )
            return result.content
    except ImportError:
        # 降级到标准方式
        from mcp.client.stdio import stdio_client
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "resolve-library",
                    arguments={"libraryName": library}
                )
                return result.content


asyncio.run(query_context7_simple("nextjs", "Server Components"))