from .agent import Agent

from langgraph.prebuilt import create_react_agent


class ReactAgent(Agent):
    @staticmethod
    def _build_graph(model, tools, prompt, checkpointer):
        return create_react_agent(
            model=model,
            prompt=prompt,
            tools=tools,
            checkpointer=checkpointer,
        )
