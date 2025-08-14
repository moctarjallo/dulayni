import click

@click.command()
@click.option("--server_host", default="127.0.0.1", help="Host to bind")
@click.option("--server_port", default=8001, help="Port to bind")
def server(server_host, server_port):
    """Start the Dulayni API server"""
    from dulayni.mcp.server import start_server
    start_server(server_host, server_port)


@click.command()
@click.option("--client_host", default="127.0.0.1", help="Host to bind")
@click.option("--client_port", default=8002, help="Port to bind")
@click.option("--debug-tools", is_flag=True, help="Enable debug mode for tools")
def client(client_host, client_port, debug_tools):
    """Start the Dulayni API client"""
    from dulayni.mcp.client import start_client
    start_client(client_host, client_port, debug_tools)
