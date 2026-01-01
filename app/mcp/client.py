import asyncio
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.core.config import settings

class MCPClientManager:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command=settings.MCP_SERVER_COMMAND,
            args=settings.MCP_SERVER_ARGS,
            env=None
        )
        self.session = None
        self._exit_stack = None

    @asynccontextmanager
    async def connect(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                yield session

    async def list_tools(self):
        if not self.session:
            raise RuntimeError("MCP Session not initialized")
        return await self.session.list_tools()