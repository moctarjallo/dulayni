import json
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI


class Agent:
    def __init__(self, role, graph, parallel_tool_calls):
        self.role = role
        self.graph = graph
        self.parallel_tool_calls = parallel_tool_calls

    @classmethod
    async def create(cls, role, model_name, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls):
        model = ChatOpenAI(model=model_name)
        srv = cls._load_server_params(mcp_servers_file)
        client = MultiServerMCPClient(srv)
        tools = await client.get_tools()
        graph = cls._build_graph(model, tools, system_prompt, checkpointer)
        return cls(role, graph, parallel_tool_calls)

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
    def _build_graph(model, tools, prompt, checkpointer):
        raise NotImplementedError("Subclasses must implement _build_graph")
