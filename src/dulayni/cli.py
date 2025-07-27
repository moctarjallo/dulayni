from typing import Optional
import click
import asyncio

from dulayni.mcp.client import run_agent

@click.command()
@click.option("--model", "-m", default="gpt-4.1-mini", 
              type=click.Choice(["gpt-4.1", "gpt-4.1-mini"]))
@click.option("--openai_api_key", "-k", required=True, envvar="OPENAI_API_KEY")
@click.option("--path2mcp_servers_file", "-mcp", type=click.Path(exists=False))
@click.option("--startup_timeout", "-t", default=10.0, type=float)
@click.option("--parallel_tool_calls", "-p", is_flag=True)
@click.option("--print_mode", default="rich", 
              type=click.Choice(["json", "rich"]))
def main(model: str, openai_api_key: str, path2mcp_servers_file: Optional[str], 
         startup_timeout: float, parallel_tool_calls: bool, print_mode: str):

    result = asyncio.run(run_agent(role="user", model="gpt-4o-mini", content="what's (3 + 5) x 12?", system_prompt="You are a helpul agent", thread_id="123", memory_db="dulayni_memory.sqlite"))
    print(result)

if __name__ == "__main__":
    main()
