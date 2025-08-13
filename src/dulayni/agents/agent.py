import json
from pathlib import Path
from typing import NotRequired, TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from fastmcp import Client
from langchain_openai import ChatOpenAI

from dulayni import utils


class Agent:
    def __init__(self, role, graph, parallel_tool_calls=0):
        self.role = role
        self.graph = graph
        self.parallel_tool_calls = parallel_tool_calls

    @classmethod
    async def create(cls, role, model_name, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls, debug_tools=False):
        model = ChatOpenAI(model=model_name)
        srv = cls._load_server_params(mcp_servers_file)
        client = MultiServerMCPClient(srv)
        tools = await client.get_tools()

        if debug_tools:
            tools = await cls.debug_tools(srv) # tools from fastmcp aren't discovered by langchain, so we use it just for debugging for now
                
        graph = cls._build_graph(model, tools, system_prompt, checkpointer)
        return cls(role, graph, parallel_tool_calls)

    @classmethod
    async def debug_tools(cls, srv):
        # convert 'streamable_http' to 'streamable-http'
        for key in srv.keys():
            srv[key]['transport'] = srv[key]['transport'].replace('_', '-')
        async with Client(srv) as client:
            fastmcp_tools = await client.list_tools()
            
            # Convert FastMCP tools to LangChain tools
            langchain_tools = await utils.convert_mcp_tools_to_langchain(fastmcp_tools, client)

            import ipdb;ipdb.set_trace()

            # result = await client.call_tool("get_weather", {'location': 'Dakar'})

        return langchain_tools


    @staticmethod
    def _load_server_params(config_source, server_name: str = ""):
        if isinstance(config_source, dict):
            cfg = config_source
        elif isinstance(config_source, str):
            try:
                # Try to parse as JSON string
                cfg = json.loads(config_source)
            except json.JSONDecodeError:
                # Fallback: treat as file path
                cfg = json.loads(Path(config_source).read_text())
        else:
            raise TypeError("mcp_servers_file must be a dict, JSON string, or file path string")

        if server_name:
            return {server_name: cfg["mcpServers"][server_name]}
        return cfg["mcpServers"]

    async def respond(self, message, thread_id):
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [{"role": self.role, "content": message}]}
        result = await self.graph.ainvoke(inputs, config=config)
        return result['messages'][-1].content

    @staticmethod
    def _build_graph(model, tools, prompt, checkpointer, state_schema=None):
        raise NotImplementedError("Subclasses must implement _build_graph")

class SubAgent(TypedDict):
    name: str
    description: str
    prompt: str
    tools: NotRequired[list[str]]
