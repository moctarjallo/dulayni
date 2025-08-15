import asyncio
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from dulayni.agents import create_agent
from dulayni.config import get_server_config

_ = load_dotenv()

# Load server configuration at startup
SERVER_CONFIG = get_server_config()
DEBUG_TOOLS = os.getenv("DEBUG_TOOLS", "false").lower() == "true"

# Default values from server config
DEFAULT_CONFIG = {
    "model": SERVER_CONFIG.get("agent", {}).get("model", "gpt-4o-mini"),
    "agent_type": SERVER_CONFIG.get("agent", {}).get("agent_type", "react"),
    "system_prompt": SERVER_CONFIG.get("agent", {}).get(
        "system_prompt", "You are a helpful agent"
    ),
    "thread_id": SERVER_CONFIG.get("memory", {}).get("thread_id", "default"),
    "memory_db": SERVER_CONFIG.get("memory", {}).get("memory_db", "data/memory.sqlite"),
    "pg_uri": SERVER_CONFIG.get("memory", {}).get("pg_uri"),
    "mcp_servers_file": SERVER_CONFIG.get(
        "mcp_servers_file", "config/mcp_servers.json"
    ),
    "startup_timeout": SERVER_CONFIG.get("agent", {}).get("startup_timeout", 10.0),
    "parallel_tool_calls": SERVER_CONFIG.get("agent", {}).get(
        "parallel_tool_calls", False
    ),
}


async def run_agent(
    agent_type: str,
    role: str,
    model: str,
    content: str,
    system_prompt: str,
    thread_id: str,
    memory_db: str,
    pg_uri: Optional[str],
    mcp_servers_file: str,
    startup_timeout: float = 10.0,
    subagents: list = [],
    parallel_tool_calls: bool = False,
):
    # Use PostgreSQL if pg_uri is provided
    if pg_uri:
        async with AsyncPostgresSaver.from_conn_string(pg_uri) as checkpointer:
            await checkpointer.setup()
            agent = await create_agent(
                agent_type=agent_type,
                role=role,
                model=model,
                system_prompt=system_prompt,
                mcp_servers_file=mcp_servers_file,
                checkpointer=checkpointer,
                subagents=subagents,
                parallel_tool_calls=parallel_tool_calls,
                debug_tools=DEBUG_TOOLS,
            )
            return await agent.respond(content, thread_id)
    # Fall back to SQLite
    else:
        async with AsyncSqliteSaver.from_conn_string(memory_db) as checkpointer:
            agent = await create_agent(
                agent_type=agent_type,
                role=role,
                model=model,
                system_prompt=system_prompt,
                mcp_servers_file=mcp_servers_file,
                checkpointer=checkpointer,
                subagents=subagents,
                parallel_tool_calls=parallel_tool_calls,
                debug_tools=DEBUG_TOOLS,
            )
            return await agent.respond(content, thread_id)


app = FastAPI(
    title="Dulayni API",
    description="RAG agent API server using MCP tools",
    version="0.1.0",
)


class AgentRequest(BaseModel):
    agent_type: Optional[str] = Field(
        default=None, description="Agent type (react or deep_react)"
    )
    role: str = Field(default="user", description="Agent role")
    model: Optional[str] = Field(
        default=None, description="Model name (gpt-4o-mini by default)"
    )
    content: str = Field(..., description="Query content")
    system_prompt: Optional[str] = Field(
        default=None, description="System prompt for the agent"
    )
    thread_id: Optional[str] = Field(
        default=None, description="Thread ID for conversation continuity"
    )
    memory_db: Optional[str] = Field(
        default=None, description="Path to SQLite memory database"
    )
    pg_uri: Optional[str] = Field(
        default=None, description="PostgreSQL URI for memory storage"
    )
    mcp_servers_file: Optional[str] = Field(
        default=None, description="Path to MCP servers config file"
    )
    startup_timeout: Optional[float] = Field(
        default=None, description="Timeout for server startup"
    )
    parallel_tool_calls: Optional[bool] = Field(
        default=None, description="Enable parallel tool calls"
    )


@app.get("/")
async def root():
    return {
        "message": "Dulayni API Server",
        "version": "0.1.0",
        "debug_tools": DEBUG_TOOLS,
        "environment": os.getenv("DULAYNI_ENV", "development"),
        "default_config": DEFAULT_CONFIG,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "debug_tools": DEBUG_TOOLS,
        "config_source": os.getenv("DULAYNI_ENV", "development"),
    }


@app.post("/run_agent")
async def run_agent_endpoint(request: AgentRequest):
    try:
        # Merge request with server defaults
        config = {
            "agent_type": request.agent_type or DEFAULT_CONFIG["agent_type"],
            "role": request.role,
            "model": request.model or DEFAULT_CONFIG["model"],
            "content": request.content,
            "system_prompt": request.system_prompt or DEFAULT_CONFIG["system_prompt"],
            "thread_id": request.thread_id or DEFAULT_CONFIG["thread_id"],
            "memory_db": request.memory_db or DEFAULT_CONFIG["memory_db"],
            "pg_uri": request.pg_uri or DEFAULT_CONFIG["pg_uri"],
            "mcp_servers_file": request.mcp_servers_file
            or DEFAULT_CONFIG["mcp_servers_file"],
            "startup_timeout": request.startup_timeout
            or DEFAULT_CONFIG["startup_timeout"],
            "parallel_tool_calls": (
                request.parallel_tool_calls
                if request.parallel_tool_calls is not None
                else DEFAULT_CONFIG["parallel_tool_calls"]
            ),
        }

        response = await run_agent(
            agent_type=config["agent_type"],
            role=config["role"],
            model=config["model"],
            content=config["content"],
            system_prompt=config["system_prompt"],
            thread_id=config["thread_id"],
            memory_db=config["memory_db"],
            pg_uri=config["pg_uri"],
            mcp_servers_file=config["mcp_servers_file"],
            parallel_tool_calls=config["parallel_tool_calls"],
        )

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_api(host: str = "0.0.0.0", port: int = 8002, debug_tools: bool = False):
    global DEBUG_TOOLS
    DEBUG_TOOLS = debug_tools
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
