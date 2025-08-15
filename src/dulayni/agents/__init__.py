from .react import React, DeepReact


async def create_agent(
    agent_type,
    role,
    model,
    system_prompt,
    mcp_servers,
    checkpointer,
    subagents=[],
    parallel_tool_calls=False,
    debug_tools=False,
):
    if agent_type == "deep_react":  # change this to new added type of agent
        agent = DeepReact(subagents=subagents)
        agent = await agent.create(
            role,
            model,
            system_prompt,
            mcp_servers,
            checkpointer,
            parallel_tool_calls,
            debug_tools,
        )
    else:  # by default
        agent = await React.create(
            role,
            model,
            system_prompt,
            mcp_servers,
            checkpointer,
            parallel_tool_calls,
            debug_tools,
        )
    return agent
