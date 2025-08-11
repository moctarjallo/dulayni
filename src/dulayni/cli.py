import requests
from typing import Optional
import click
from rich.console import Console
from rich.markdown import Markdown

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
@click.option("--system_prompt", "-s", default=None,
              help="Custom system prompt for the agent")
@click.option("--api_url", default="http://127.0.0.1:8002/run_agent",
              help="URL of the Dulayni API server")
def main(model: str, openai_api_key: str,
         query: str,
         path2mcp_servers_file: str,
         startup_timeout: float,
         parallel_tool_calls: bool,
         agent_type: str,
         print_mode: str,
         system_prompt: Optional[str],
         api_url: str):
    
    effective_system_prompt = system_prompt if system_prompt is not None else "You are a helpful agent"
    
    def run_query(content: str):
        """Utilise l'API pour exécuter la requête"""
        payload = {
            "agent_type": agent_type,
            "role": "user",
            "model": model,
            "content": content,
            "system_prompt": effective_system_prompt,
            "thread_id": "123",
            "memory_db": "memory.sqlite",
            "mcp_servers_file": path2mcp_servers_file,
            "startup_timeout": startup_timeout,
            "parallel_tool_calls": parallel_tool_calls
        }
        
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}"

    if query:
        result = run_query(query)
        if print_mode == "json":
            import json
            print(json.dumps(result, indent=2))
        else:
            console.print(Markdown(result))
    else:
        console.print("[bold green]Interactive mode. Type 'q' to quit.[/bold green]")
        console.print(f"[yellow]Using API endpoint: {api_url}[/yellow]")
        while True:
            user_input = console.input("[bold blue]> [/bold blue]")
            if user_input.strip().lower() == "q":
                break
            result = run_query(user_input)
            console.print(Markdown(result))

if __name__ == "__main__":
    main()
