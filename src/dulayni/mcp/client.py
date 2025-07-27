import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from dulayni.agents import ReactAgent

_ = load_dotenv()


server_params = StdioServerParameters(
    command="python",
    args=["src/dulayni/mcp/server.py"],
)

async def run_agent(role, model, content, system_prompt, thread_id, memory_db):
    # Set up persistent memory saver
    async with AsyncSqliteSaver.from_conn_string(memory_db) as checkpointer:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)

                agent = ReactAgent(role, model, system_prompt, tools, checkpointer)

                return await agent.respond(content, thread_id)

# Run the async function
if __name__ == "__main__":
    result = asyncio.run(run_agent(role="user", model="gpt-4o-mini", content="what's (3 + 5) x 12?", system_prompt="You are a helpul agent", thread_id=123, memory_db="dulayni_memory.sqlite"))
    print(result)
