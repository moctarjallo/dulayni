# math_server.py
from fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def get_weather(location: str) -> str:
    """Get weather information for a location"""
    return f"The weather in {location} today is very hot."

def start_server(host: str = "0.0.0.0", port: int = 8001):
    mcp.run(transport='streamable-http', stateless_http=True, host=host, port=port)

if __name__ == "__main__":
    start_server()
