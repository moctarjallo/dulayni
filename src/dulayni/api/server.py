from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from dulayni.agents import create_agent

_ = load_dotenv()

app = FastAPI(title="Dulayni API")

class AgentRequest(BaseModel):
    agent_type: str
    role: str
    model: str
    content: str
    system_prompt: str
    thread_id: str
    memory_db: str
    mcp_servers_file: str
    startup_timeout: float = 10.0
    parallel_tool_calls: bool = False

@app.post("/run_agent")
async def run_agent_endpoint(request: AgentRequest):
    async with AsyncSqliteSaver.from_conn_string(request.memory_db) as checkpointer:
        agent = await create_agent(
            agent_type=request.agent_type,
            role=request.role,
            model=request.model,
            system_prompt=request.system_prompt,
            mcp_servers_file=request.mcp_servers_file,
            checkpointer=checkpointer,
            parallel_tool_calls=request.parallel_tool_calls,
        )
        response = await agent.respond(request.content, request.thread_id)
        return {"response": response}

def start_server(host: str = "127.0.0.1", port: int = 8002):
    uvicorn.run(app, host=host, port=port)
