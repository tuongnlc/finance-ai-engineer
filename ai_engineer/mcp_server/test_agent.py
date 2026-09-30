import operator
import asyncio
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

api_key = os.getenv("GCP_PROJECT_1")


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=api_key,
    temperature=0,
    max_retries=0,
)

async def _connect_tool(adapter: MCPAdapter):
    all_tools = await adapter.list_tools()
    tools = [t for t in all_tools if t.name == "get_current_weather"]
    tool_map = {t.name: t for t in tools}
    return tools, tool_map

async def main():
    async with MCPAdapter("http://127.0.0.1:8000/sse") as adapter:
        # all_tools = await adapter.list_tools()
        # tools = [t for t in all_tools if t.name == "get_current_weather"]
        # tool_map = {t.name: t for t in tools}
        tools, tool_map = await _connect_tool(adapter)


        model_with_tools = model.bind_tools(tools)

        async def call_model(state: AgentState):
            messages = state["messages"]
            response = await model_with_tools.ainvoke(messages)
            return {"messages": [response]}

        async def call_tools(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]

            tool_messages = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_to_invoke = tool_map[tool_name]

                tool_output = await tool_to_invoke.ainvoke(tool_args)

                tool_messages.append(
                    ToolMessage(
                        content=str(tool_output),
                        tool_call_id=tool_call["id"],
                    )
                )
            return {"messages": tool_messages}

        def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
            """
                Determine if the agent should continue with the tools or end.

                Logic is if the last message has tool_calls, then continue with the tools.
                Otherwise, end the workflow.
            """
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.tool_calls:
                return "tools"
            return END

        workflow = StateGraph(AgentState)

        workflow.add_node("agent", call_model)
        workflow.add_node("tools", call_tools)

        workflow.add_edge(START, "agent")

        workflow.add_conditional_edges(
            "agent",
            should_continue,
        )

        workflow.add_edge("tools", "agent")

        app = workflow.compile()

        inputs = {"messages": [HumanMessage(content="What's the weather like in Tokyo right now?")]}
        output = await app.ainvoke(inputs)

        for message in output["messages"]:
            message.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
