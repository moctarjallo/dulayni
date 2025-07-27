import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

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
            parallel_tool_calls=parallel_tool_calls,
        )

        return await agent.respond(content, thread_id)

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
