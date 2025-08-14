import click


@click.command()
@click.option("--server_host", default="127.0.0.1", help="Host to bind")
@click.option("--server_port", default=8001, help="Port to bind")
def server(server_host, server_port):
    """Start the Dulayni API server"""
    from dulayni.mcp.server import start_server

    start_server(server_host, server_port)


@click.command()
@click.option("--api_host", default="127.0.0.1", help="Host to bind")
@click.option("--api_port", default=8002, help="Port to bind")
@click.option("--debug-tools", is_flag=True, help="Enable debug mode for tools")
def api(api_host, api_port, debug_tools):
    """Start the Dulayni API client"""
    from dulayni.mcp.api import start_api

    start_api(api_host, api_port, debug_tools)
