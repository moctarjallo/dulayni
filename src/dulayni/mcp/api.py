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
    "mcp_servers": {
        "mcpServers": SERVER_CONFIG.get("mcpServers", {}),
    },
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
    mcp_servers: Dict[str, Any],
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
                mcp_servers=mcp_servers,
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
                mcp_servers=mcp_servers,
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
    mcp_servers: Optional[Dict[str, Any]] = Field(
        default=None, description="MCP servers configuration"
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


def merge_mcp_servers(default_servers: Dict[str, Any], request_servers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge MCP servers with priority given to request values."""

    if not request_servers:
        return default_servers.copy()
    
    merged = default_servers.copy()
    merged["mcpServers"].update(request_servers)
    return merged


@app.post("/run_agent")
async def run_agent_endpoint(request: AgentRequest):
    try:
        # Merge MCP servers with priority to request values
        merged_mcp_servers = merge_mcp_servers(
            DEFAULT_CONFIG["mcp_servers"], 
            request.mcp_servers
        )
        
        # Merge request with server defaults (request values always have priority)
        config = {
            "agent_type": request.agent_type if request.agent_type is not None else DEFAULT_CONFIG["agent_type"],
            "role": request.role,  # role is always required, no default needed
            "model": request.model if request.model is not None else DEFAULT_CONFIG["model"],
            "content": request.content,  # content is always required
            "system_prompt": request.system_prompt if request.system_prompt is not None else DEFAULT_CONFIG["system_prompt"],
            "thread_id": request.thread_id if request.thread_id is not None else DEFAULT_CONFIG["thread_id"],
            "memory_db": request.memory_db if request.memory_db is not None else DEFAULT_CONFIG["memory_db"],
            "pg_uri": request.pg_uri if request.pg_uri is not None else DEFAULT_CONFIG["pg_uri"],
            "mcp_servers": merged_mcp_servers,
            "startup_timeout": request.startup_timeout if request.startup_timeout is not None else DEFAULT_CONFIG["startup_timeout"],
            "parallel_tool_calls": request.parallel_tool_calls if request.parallel_tool_calls is not None else DEFAULT_CONFIG["parallel_tool_calls"],
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
            mcp_servers=config["mcp_servers"],
            startup_timeout=config["startup_timeout"],
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
