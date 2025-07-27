from typing import Optional
import click
import asyncio
from rich.console import Console
from rich.markdown import Markdown

from dulayni.mcp.client import run_agent

console = Console()

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
    async def handle_query(content: str):
        return await run_agent(
            agent_type=agent_type,
            role="user",
            model=model,
            content=content,
            system_prompt="You are a helpful agent",
            thread_id="123",
            memory_db="dulayni_memory.sqlite",
            mcp_servers_file=path2mcp_servers_file,
            startup_timeout=startup_timeout,
            parallel_tool_calls=parallel_tool_calls
        )

    if query:
        result = asyncio.run(handle_query(query))
        if print_mode == "json":
            import json
            print(json.dumps(result, indent=2))
        else:
            console.print(Markdown(result))
    else:
        console.print("[bold green]Interactive mode. Type 'q' to quit.[/bold green]")
        while True:
            user_input = console.input("[bold blue]> [/bold blue]")
            if user_input.strip().lower() == "q":
                break
            result = asyncio.run(handle_query(user_input))
            console.print(Markdown(result))


if __name__ == "__main__":
    main()
