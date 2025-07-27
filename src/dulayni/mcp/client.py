import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from dulayni.agents import Agent

_ = load_dotenv()

def load_server_params(config_path: str, server_name: str = "default"):
    cfg = json.loads(Path(config_path).read_text())
    if server_name:
        return {
            server_name: cfg["mcpServers"][server_name]
        }
    return cfg["mcpServers"]
    

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
        srv = load_server_params(mcp_servers_file)
        client = MultiServerMCPClient(srv)
        tools = await client.get_tools()

        agent = Agent.create_agent(
            agent_type=agent_type,
            role=role,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
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
