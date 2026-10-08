import json
import operator
import asyncio
import sys
import warnings
import logging
from pathlib import Path
from typing import Annotated, Literal, TypedDict
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage, HumanMessage, convert_to_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv
import os
import mlflow
import requests

from ai_engineer.applications.chatbot.applications.prompt.prompt_loading import ChatbotPromptLoading
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

warnings.filterwarnings("ignore", message="Key 'additionalProperties' is not supported in schema, ignoring")
logging.getLogger().addFilter(lambda r: "additionalProperties" not in r.getMessage())

_w = sys.stdout.write
sys.stdout.write = lambda s, _orig=_w: _orig(s) if "additionalProperties" not in s else None
_e = sys.stderr.write
sys.stderr.write = lambda s, _orig=_e: _orig(s) if "additionalProperties" not in s else None

mlflow.langchain.autolog()
mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("tracing_agent_new")

prompt_register = PromptRegister()
prompt_template = prompt_register.load_and_parse_prompt('tool_calling_prompt_v1')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

api_key = os.getenv("GCP_PROJECT_1")


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

class ToolOutput(BaseModel):
    tool_output: str
    tool_name: str
    input_message: str

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=api_key,
    temperature=0,
)

async def _connect_tool(adapter: MCPAdapter):
    all_tools = await adapter.list_tools()
    tool_map = {t.name: t for t in all_tools}
    return all_tools, tool_map


url = "http://localhost:8000/ai_chat/query_understand/"
headers = {
    "accept": "*/*",
    "Content-Type": "application/json"
}


async def query_transformation(content: str):
    """
    Transform user query to JSON format.
    """
    payload = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "content": content,
        "question_context": None
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        preprocessed_query = data.get("response", data)

        print(data)

    else:
        raise RuntimeError(f"query_transformation failed: {response.status_code}")
    return preprocessed_query

async def call_agent(preprocessed_query: str):
    async with MCPAdapter("http://127.0.0.1:7000/sse") as adapter:
        tools, tool_map = await _connect_tool(adapter)

        model_with_tools = model.bind_tools(tools)
        model_structured = model.with_structured_output(ToolOutput)

        async def call_model(state: AgentState):
            msgs = convert_to_messages(state["messages"])
            user_msg = [m for m in msgs if m.type == "human"][-1]
            has_tool_msg = any(m.type == "tool" for m in msgs)
            messages = prompt_template.format_messages(input=user_msg.content)
            messages += [m for m in msgs if m.type != "human"]

            if has_tool_msg:
                response_obj = await model_structured.ainvoke(messages)
                return {"messages": [AIMessage(content=response_obj.model_dump_json())]}
            response = await model_with_tools.ainvoke(messages)
            return {"messages": [response]}

        async def call_tools(state: AgentState):
            messages = convert_to_messages(state["messages"])
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
            messages = convert_to_messages(state["messages"])
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

        output = await app.ainvoke({"messages": [{"role": "user", "content": preprocessed_query}]})

        messages = convert_to_messages(output.get("messages", []))
        for msg in reversed(messages):
            if msg.type == "ai" and isinstance(msg.content, str):
                import json as _json
                try:
                    parsed = _json.loads(msg.content)
                    return ToolOutput(**parsed).model_dump()
                except Exception:
                    raise RuntimeError(f"call_agent failed to parse output: {msg.content}")
        raise RuntimeError("call_agent failed: no AI response found")

async def main():
    content = "Tin tuc thi truong gan day ve ngan hang ACB"
    preprocessed_query = await query_transformation(content)
    # print(preprocessed_query)
    response = await call_agent(preprocessed_query)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
