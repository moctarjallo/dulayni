import click

@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=8002, help="Port to bind")
def server(host, port):
    """Start the Dulayni API server"""
    from dulayni.mcp.client import start_server
    start_server(host, port)
