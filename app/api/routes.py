import time
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph.agent import build_graph
from app.mcp.client import MCPClientManager
from app.core.config import settings

router = APIRouter()
start_time = time.time()  # Track when server started

class QueryRequest(BaseModel):
    query: str

# Initialize the MCP Client Manager
mcp_manager = MCPClientManager()

# --- 1. Executive Dashboard ---
@router.get("/dashboard")
async def get_dashboard_stats():
    """
    Executive Dashboard: High-level overview of the system status.
    Shows uptime, connected model, and active MCP capabilities.
    """
    try:
        # Calculate Uptime
        uptime_seconds = int(time.time() - start_time)
        
        # Get Tool Information
        async with mcp_manager.connect() as session:
            tools = await session.list_tools()
            tool_count = len(tools.tools)
            tool_names = [t.name for t in tools.tools]

        return {
            "system_status": "healthy",
            "uptime_seconds": uptime_seconds,
            "connected_mcp_server": settings.MCP_SERVER_COMMAND,
            "ai_model": settings.OPENAI_MODEL,
            "active_capabilities": {
                "count": tool_count,
                "tools": tool_names[:5] + ["..."] if tool_count > 5 else tool_names
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# --- 2. Health Check ---
@router.get("/health")
async def health_check():
    """
    Production standard: Checks if the app is running.
    """
    return {"status": "ok", "service": "mcp-langgraph-agent"}

# --- 3. Tool Inspection ---
@router.get("/mcp/tools")
async def list_active_tools():
    """
    Lists all tools currently available to the Agent via MCP.
    This demonstrates the 'Universal Connectivity' of the protocol.
    """
    try:
        async with mcp_manager.connect() as session:
            tools = await session.list_tools()
            
            # Format the output nicely
            tool_list = []
            for t in tools.tools:
                tool_list.append({
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                })
            
            return {
                "count": len(tool_list),
                "source": "MCP FileSystem Server",
                "tools": tool_list
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. Main Chat Endpoint ---
@router.post("/chat")
async def chat_endpoint(request: QueryRequest):
    """
    Triggers the LangGraph agent with a user query.
    Connects to MCP -> Builds Graph -> Executes -> Returns Answer.
    """
    try:
        # 1. Connect to MCP Server
        async with mcp_manager.connect() as session:
            
            # 2. Build the graph with the active MCP connection
            app = await build_graph(mcp_manager)
            
            # 3. Run the graph
            # Initialize state with the user's message
            initial_state = {"messages": [("user", request.query)]}
            
            # We use ainvoke (async invoke)
            result = await app.ainvoke(initial_state)
            
            # 4. Extract the final response
            final_message = result["messages"][-1].content
            return {"response": final_message}

    except Exception as e:
        # --- DEBUGGING BLOCK ---
        # This captures the full error stack and sends it to the browser/client
        # so you can see exactly why it crashed (e.g. RecursionError, API Key missing)
        full_error = traceback.format_exc()
        print("❌ CRITICAL ERROR CAUGHT:\n", full_error)
        raise HTTPException(status_code=500, detail=f"REAL ERROR FOUND:\n{full_error}")