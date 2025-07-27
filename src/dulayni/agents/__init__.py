from .react import ReactAgent

async def create_agent(agent_type, role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls):
    if agent_type=="react": # change this to new added type of agent
        return await ReactAgent.create(role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls)
    else: # by default
        return await ReactAgent.create(role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls)
