from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class ReactAgent:
    def __init__(self, role, model, system_prompt, tools, checkpointer, parallel_tool_calls):
        model = ChatOpenAI(model=model)
        self.agent = create_react_agent(
            model=model,
            prompt=system_prompt,
            tools=tools,
            checkpointer=checkpointer,
        )    
        self.role = role
        self.parallel_tool_calls = parallel_tool_calls

    async def respond(self, message, thread_id):
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [{"role": self.role, "content": message}]}
        result = await self.agent.ainvoke(inputs, config=config)
        return result['messages'][-1].content
