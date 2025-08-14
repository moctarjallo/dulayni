from dulayni.graph.state import DeepReactState
from dulayni.prompts import TASK_DESCRIPTION_PREFIX, TASK_DESCRIPTION_SUFFIX, base_prompt
from dulayni.tools import edit_file, ls, read_file, write_file, write_todos
from .agent import Agent, SubAgent

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
from typing import TypedDict
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from typing import Annotated, NotRequired
from langgraph.types import Command

from langgraph.prebuilt import InjectedState

class React(Agent):
    @staticmethod
    def _build_graph(model, tools, prompt, checkpointer, state_schema=None):
        return create_react_agent(
            model=model,
            prompt=prompt,
            tools=tools,
            checkpointer=checkpointer,
            state_schema=state_schema
        )
    
class DeepReact(Agent):
    subagents: list[SubAgent] = []

    def __init__(self, role: str='', graph=None, parallel_tool_calls=False, subagents: list[SubAgent] = [], *args, **kwargs):
        super().__init__(role, graph, parallel_tool_calls)
        if subagents is not None:
            DeepReact.subagents = subagents


    @staticmethod
    def _create_task_tool(tools, instructions, subagents: list[SubAgent], model, state_schema):
        agents = {
            "general-purpose": create_react_agent(model, prompt=instructions, tools=tools)
        }
        tools_by_name = {}
        for tool_ in tools:
            if not isinstance(tool_, BaseTool):
                tool_ = tool(tool_)
            tools_by_name[tool_.name] = tool_
        for _agent in subagents:
            if "tools" in _agent:
                _tools = [tools_by_name[t] for t in _agent["tools"]]
            else:
                _tools = tools
            agents[_agent["name"]] = create_react_agent(
                model, prompt=_agent["prompt"], tools=_tools, state_schema=state_schema
            )

        other_agents_string = [
            f"- {_agent['name']}: {_agent['description']}" for _agent in subagents
        ]

        @tool(
            description=TASK_DESCRIPTION_PREFIX.format(other_agents=other_agents_string)
            + TASK_DESCRIPTION_SUFFIX
        )
        def task(
            description: str,
            subagent_type: str,
            state: Annotated[DeepReactState, InjectedState],
            tool_call_id: Annotated[str, InjectedToolCallId],
        ):
            if subagent_type not in agents:
                return f"Error: invoked agent of type {subagent_type}, the only allowed types are {[f'`{k}`' for k in agents]}"
            sub_agent = agents[subagent_type]
            state["messages"] = [{"role": "user", "content": description}]
            result = sub_agent.invoke(state)
            return Command(
                update={
                    "files": result.get("files", {}),
                    "messages": [
                        ToolMessage(
                            result["messages"][-1].content, tool_call_id=tool_call_id
                        )
                    ],
                }
            )

        return task

    @staticmethod
    def _build_graph(model, tools, prompt, checkpointer, state_schema=None):
        """Create a deep agent.

            This agent will by default have access to a tool to write todos (write_todos),
            and then four file editing tools: write_file, ls, read_file, edit_file.

            Args:
                tools: The additional tools the agent should have access to.
                instructions: The additional instructions the agent should have. Will go in
                    the system prompt.
                model: The model to use.
                subagents: The subagents to use. Each subagent should be a dictionary with the
                    following keys:
                        - `name`
                        - `description` (used by the main agent to decide whether to call the sub agent)
                        - `prompt` (used as the system prompt in the subagent)
                        - (optional) `tools`
                state_schema: The schema of the deep agent. Should subclass from DeepReactState
            """
        prompt = prompt + base_prompt
        built_in_tools = [write_todos, write_file, read_file, ls, edit_file]
        state_schema = state_schema or DeepReactState
        task_tool = DeepReact._create_task_tool(
            list(tools) + built_in_tools,
            prompt,
            DeepReact.subagents or [],
            model,
            state_schema
        )
        all_tools = built_in_tools + list(tools) + [task_tool]
        
        return create_react_agent(
            model,
            prompt=prompt,
            tools=all_tools,
            checkpointer=checkpointer,
            state_schema=state_schema,
        )
