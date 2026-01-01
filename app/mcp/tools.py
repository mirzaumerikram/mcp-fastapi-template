from langchain_core.tools import StructuredTool
from app.mcp.client import MCPClientManager
from pydantic import create_model, Field
from typing import Any, Type, List

def create_tool_schema(schema_model: dict) -> Type:
    """
    Dynamically converts MCP JSON Schema to a Pydantic Model.
    """
    fields = {}
    required_fields = schema_model.get("required", [])
    
    if "properties" in schema_model:
        for field_name, field_info in schema_model["properties"].items():
            field_type = str 
            description = field_info.get("description", "")
            
            if field_name in required_fields:
                default_val = ... 
            else:
                default_val = None
                
            fields[field_name] = (field_type, Field(default=default_val, description=description))
            
    return create_model("DynamicToolInput", **fields)

def convert_mcp_tool_to_langchain(mcp_tool_schema, mcp_client: MCPClientManager):
    """
    Creates a LangChain StructuredTool with a proper Pydantic schema.
    """
    tool_name = mcp_tool_schema.name
    description = mcp_tool_schema.description
    input_schema = mcp_tool_schema.inputSchema

    args_schema = create_tool_schema(input_schema)

    async def wrapped_tool_func(**kwargs):
        if not mcp_client.session:
            return "Error: MCP Client not connected."
        
        # Clean up args: Remove None values so we don't send nulls to the server
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        print(f"🛠️ AI Calling Tool: {tool_name} with args: {clean_kwargs}")
        
        try:
            result = await mcp_client.session.call_tool(tool_name, arguments=clean_kwargs)
            
            if hasattr(result, 'content') and result.content:
                text_content = []
                for item in result.content:
                    if hasattr(item, "text"):
                        text_content.append(item.text)
                
                final_output = "\n".join(text_content)
                
                # --- DEBUGGING LINE ADDED ---
                print(f"   ✅ Tool Output Preview: {final_output[:200]}...") 
                # ----------------------------
                
                return final_output
            
            return str(result)
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            print(f"   ❌ Tool Failed: {error_msg}")
            return error_msg

    return StructuredTool.from_function(
        func=None,
        coroutine=wrapped_tool_func,
        name=tool_name,
        description=description,
        args_schema=args_schema
    )