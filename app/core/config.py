import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "MCP LangGraph Starter"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"  # Enforced model
    
    # MCP Configuration (Defaults to local filesystem server for demo)
    # You need Node.js installed for this default command
# Use npx.cmd for Windows, npx for Mac/Linux
    MCP_SERVER_COMMAND: str = "npx.cmd"
    MCP_SERVER_ARGS: list = ["-y", "@modelcontextprotocol/server-filesystem", "./"]

settings = Settings()