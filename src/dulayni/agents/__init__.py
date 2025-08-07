from .react import ReactAgent, DeepAgent

async def create_agent(agent_type, role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls):
    if agent_type=="deep_agent": # change this to new added type of agent
        agent = await DeepAgent.create(role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls)
    else: # by default
        agent = await ReactAgent.create(role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls)
    return agent