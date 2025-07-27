from .react import ReactAgent


class Agent:
    @classmethod
    def create_agent(cls, agent_type, role, model, system_prompt, tools, checkpointer, parallel_tool_calls):
        if agent_type=="react": # change this to new added type of agent
            return ReactAgent(role, model, system_prompt, tools, checkpointer, parallel_tool_calls)
        else: # by default
            return ReactAgent(role, model, system_prompt, tools, checkpointer, parallel_tool_calls)
