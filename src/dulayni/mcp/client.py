import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from dulayni.agents import create_agent

_ = load_dotenv()

 
async def run_agent(
    agent_type: str,
    role: str,
    model: str,
    content: str,
    system_prompt: str,
    thread_id: str,
    memory_db: str,
    mcp_servers_file: str,
    startup_timeout: float = 10.0,
    subagents: list = [],
    parallel_tool_calls: bool = False,
):   
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
        )

        return await agent.respond(content, thread_id)

app = FastAPI(
    title="Dulayni API",
    description="RAG agent API server using MCP tools",
    version="0.1.0"
)

class AgentRequest(BaseModel):
    agent_type: str = "react"
    role: str = "user"
    model: str = "gpt-4o-mini"
    content: str
    system_prompt: str = "You are a helpful agent"
    thread_id: str = "default"
    memory_db: str = "data/memory.sqlite"
    mcp_servers_file: str = "config/mcp_servers.json"
    startup_timeout: float = 10.0
    parallel_tool_calls: bool = False

@app.get("/")
async def root():
    return {"message": "Dulayni API Server", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/run_agent")
async def run_agent_endpoint(request: AgentRequest):
    try:
        response = await run_agent(
            agent_type=request.agent_type,
            role=request.role,
            model=request.model,
            content=request.content,
            system_prompt=request.system_prompt,
            thread_id=request.thread_id,
            memory_db=request.memory_db,
            mcp_servers_file=request.mcp_servers_file,
            parallel_tool_calls=request.parallel_tool_calls,
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_server(host: str = "0.0.0.0", port: int = 8002):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
