import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

_ = load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

server_params = StdioServerParameters(
    command="python",
    args=["src/dulayni/mcp/server.py"],
)

async def run_agent(role, content, thread_id, memory_db):
    # Set up persistent memory saver
    async with AsyncSqliteSaver.from_conn_string(memory_db) as checkpointer:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)

                # Create the ReAct agent with persistence
                agent = create_react_agent(
                    model=model,
                    tools=tools,
                    checkpointer=checkpointer,
                )

                # Use a named thread for memory persistence
                config = {"configurable": {"thread_id": thread_id}}

                inputs = {"messages": [{"role": role, "content": content}]}
                result = await agent.ainvoke(inputs, config=config)

                return result

# Run the async function
if __name__ == "__main__":
    result = asyncio.run(run_agent(role="user", content="what's (3 + 5) x 12?", thread_id=123, memory_db="dulayni_memory.sqlite"))
    print(result['messages'][-1].content)
