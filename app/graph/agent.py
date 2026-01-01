from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.graph.state import AgentState
from app.mcp.client import MCPClientManager
from app.mcp.tools import convert_mcp_tool_to_langchain
from app.core.config import settings

async def build_graph(mcp_client: MCPClientManager):
    # 1. Initialize Model
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)

    # 2. Fetch Tools safely
    try:
        mcp_tools_list = await mcp_client.list_tools()
        tools = [convert_mcp_tool_to_langchain(t, mcp_client) for t in mcp_tools_list.tools]
        llm_with_tools = llm.bind_tools(tools)
    except Exception as e:
        print(f"Error binding tools: {e}")
        llm_with_tools = llm
        tools = []

    # 3. Define Nodes
    # STRICTER PROMPT: We tell it exactly how to use the filesystem
    prompt_content = """You are a helpful assistant. 
    You have access to a filesystem via tools. 
    IMPORTANT: When using 'list_directory' or 'read_file', you MUST provide the 'path' argument.
    The current directory is denoted by '.'
    Start by listing the files in '.' to orient yourself.
    """
    sys_msg = SystemMessage(content=prompt_content)

    def call_model_node(state):
        messages = [sys_msg] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # 4. Build Graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model_node)
    
    if tools:
        workflow.add_node("tools", ToolNode(tools))
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges("agent", should_continue)
    else:
        workflow.add_edge("agent", END)

    workflow.set_entry_point("agent")
    
    return workflow.compile()