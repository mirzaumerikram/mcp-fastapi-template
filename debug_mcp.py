import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment to check API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"1. Checking API Key: {'Found ✅' if api_key else 'MISSING ❌'}")

async def run_debug():
    print("2. Attempting to start MCP Server (npx.cmd)...")
    
    # Define server parameters explicitly
    server_params = StdioServerParameters(
        command="npx.cmd",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            print("   -> Connection established! (Stdio pipes open)")
            
            async with ClientSession(read, write) as session:
                print("   -> Initializing Session...")
                await session.initialize()
                print("   -> Session Initialized! ✅")
                
                print("3. Listing Tools...")
                tools = await session.list_tools()
                print(f"   -> Success! Found {len(tools.tools)} tools.")
                for t in tools.tools:
                    print(f"      - {t.name}")

    except Exception as e:
        print(f"\n❌ ERROR CAUGHT: {type(e).__name__}")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    asyncio.run(run_debug())