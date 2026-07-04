"""Drive the Legacy MCP server over stdio like a real client would."""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command="/Users/sarveshwaran/hangover/.venv/bin/python",
        args=["-m", "app.mcp_server"],
        cwd="/Users/sarveshwaran/hangover/backend",
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            r = await session.call_tool("legacy_alignment", {})
            print("ALIGNMENT:", r.content[0].text)
            r = await session.call_tool("legacy_recall",
                {"question": "what tech stack did the user use in project app-a?"})
            print("RECALL:", r.content[0].text[:400])

asyncio.run(main())
