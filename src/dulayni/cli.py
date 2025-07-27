from typing import Optional
import click
import asyncio

from dulayni.mcp.client import run_agent

@click.command()
@click.option("--model", "-m", default="gpt-4.1-mini",
              type=click.Choice(["gpt-4.1", "gpt-4.1-mini"]))
@click.option("--openai_api_key", "-k", required=True, envvar="OPENAI_API_KEY")
@click.option("--query", "-q", type=str, required=False)
@click.option("--path2mcp_servers_file", "-mcp", default="config/mcp_servers.json",
              type=click.Path(exists=True))
@click.option("--startup_timeout", "-t", default=10.0, type=float)
@click.option("--parallel_tool_calls", "-p", is_flag=True)
@click.option("--agent_type", "-a", default="react")
@click.option("--print_mode", default="rich",
              type=click.Choice(["json", "rich"]))
def main(model: str, openai_api_key: str,
         query: str,
         path2mcp_servers_file: str,
         startup_timeout: float,
         parallel_tool_calls: bool,
         agent_type: str,
         print_mode: str):
    # You can load the API key in env or pass it into run_agent if needed
    query = query or "what's (3 + 5) x 12?"
    result = asyncio.run(run_agent(
        agent_type=agent_type,
        role="user",
        model=model,
        content=query,
        system_prompt="You are a helpful agent",
        thread_id="123",
        memory_db="dulayni_memory.sqlite",
        mcp_servers_file=path2mcp_servers_file,
        startup_timeout=startup_timeout,
        parallel_tool_calls=parallel_tool_calls
    ))
    if print_mode == "json":
        import json
        print(json.dumps(result, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
