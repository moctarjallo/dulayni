from .react import ReactAgent, DeepAgent

async def create_agent(agent_type, role, model, system_prompt, mcp_servers_file, checkpointer, subagents=[], parallel_tool_calls=False):
    if agent_type=="deep_agent": # change this to new added type of agent
        agent = DeepAgent(subagents=subagents)
        agent = await agent.create(role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls)
    else: # by default
        agent = await ReactAgent.create(role, model, system_prompt, mcp_servers_file, checkpointer, parallel_tool_calls)
    return agent