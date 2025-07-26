from typing import Optional
import click
import asyncio

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
    print(f"OPENAI_API_KEY: {openai_api_key}")
    pass

if __name__ == "__main__":
    main()
