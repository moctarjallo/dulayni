from fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun

mcp = FastMCP("Dulayni")

@mcp.tool()
def get_weather(location: str) -> str:
    """Get weather information for a location"""
    return f"The weather in {location} today is very hot."


@mcp.tool()
def search_web(query: str) -> str:
    """Use this tool to search the web"""
    search = DuckDuckGoSearchRun()
    return search.invoke(query)


def start_server(host: str = "0.0.0.0", port: int = 8001):
    mcp.run(transport="streamable-http", stateless_http=True, host=host, port=port)


if __name__ == "__main__":
    start_server()
