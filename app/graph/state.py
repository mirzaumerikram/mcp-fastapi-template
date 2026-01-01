from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'messages' will store the chat history (HumanMessage, AIMessage, etc.)
    # add_messages is a reducer that appends new messages to the list
    messages: Annotated[List[Any], add_messages]
    
    # You can add other state variables here (e.g., 'user_id', 'context')
    # context: str