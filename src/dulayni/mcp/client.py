import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from fastapi import FastAPI
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

def start_server(host: str = "127.0.0.1", port: int = 8002):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    result = asyncio.run(run_agent(
        agent_type="react",
        role="user",
        model="gpt-4o-mini",
        content="what's (3 + 5) x 12?",
        system_prompt="You are a helpful agent",
        thread_id=123,
        memory_db="dulayni_memory.sqlite",
        mcp_servers_file="config/mcp_servers.json",
    ))
    print(result)
