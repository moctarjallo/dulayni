# math_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math", stateless_http=True, host="127.0.0.1", port=8001)

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
    return f"The weather in {location} today is very hot."

@mcp.tool()
def galsenai():
    """Return information about Galsen AI"""
    text = ""

    with open('./galsenai.txt', 'r') as f:

        text = f.read()

    print(f"text: {text}")

    return text

if __name__ == "__main__":
    mcp.run(transport='streamable-http')
