from fastapi import FastAPI
from app.api import routes
from contextlib import asynccontextmanager
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup: MCP LangGraph Template Initialized 🚀")
    yield
    print("Shutdown: Cleaning up...")

# Professional Metadata
app = FastAPI(
    title="Evren AI - MCP Starter Template",
    description="A modular boilerplate for building AI Agents using LangGraph and the Model Context Protocol (MCP).",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(routes.router)

@app.get("/")
def root():
    return {
        "message": "MCP Server Running",
        "docs": "/docs",
        "health": "/health"
    }