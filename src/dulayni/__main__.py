from dulayni.mcp.cli import server
from dulayni.mcp.cli import client
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    server()
