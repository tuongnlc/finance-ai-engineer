import operator
import json as _json
from threading import RLock
from typing import Annotated, Literal, TypedDict
import mlflow

from langchain_core.messages import BaseMessage, ToolMessage, AIMessage, convert_to_messages
from langgraph.graph import END, START, StateGraph
from langchain.mcp import MCPAdapter
from pydantic import BaseModel

from ai_engineer.shared.llm.create_llm import create_gemini_llm
from ai_engineer.applications.chatbot.applications.io_schemas import ToolCallingOutput
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


class AgentCallerService:
    _lock = RLock()
    _prompts: dict[str, object] = {}
    _llm_cache: dict[tuple[str, str, float], object] = {}

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        prompt_name: str,
        mcp_server_url: str = "http://127.0.0.1:7000/sse",
        pydantic_object: type[BaseModel] = ToolCallingOutput,
    ):
        self._config = (api_key, model_name, temperature)
        self.llm = self._get_llm(api_key, model_name, temperature)
        self.prompt_name = prompt_name
        self.mcp_server_url = mcp_server_url
        self._pydantic_object = pydantic_object
        mlflow.langchain.autolog()
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("tracing_agent_new")

    def _get_prompt(self):
        key = self.prompt_name
        if key in self.__class__._prompts:
            return self.__class__._prompts[key]

        with self.__class__._lock:
            if key not in self.__class__._prompts:
                prompt = PromptRegister().load_and_parse_prompt(self.prompt_name)
                self.__class__._prompts[key] = prompt
        return self.__class__._prompts[key]

    @classmethod
    def _get_llm(cls, api_key: str, model_name: str, temperature: float):
        key = (api_key, model_name, temperature)
        cached = cls._llm_cache.get(key)
        if cached is not None:
            return cached

        with cls._lock:
            cached = cls._llm_cache.get(key)
            if cached is None:
                cached = create_gemini_llm(api_key, model_name, temperature)
                cls._llm_cache[key] = cached
        return cached

    async def call_agent(self, preprocessed_query: str) -> dict:
        prompt_template = self._get_prompt()
        model = self.llm

        async with MCPAdapter(self.mcp_server_url) as adapter:
            all_tools = await adapter.list_tools()
            tool_map = {t.name: t for t in all_tools}

            model_with_tools = model.bind_tools(all_tools)
            model_structured = model.with_structured_output(self._pydantic_object)

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
                if response.tool_calls:
                    return {"messages": [response]}
                response_obj = await model_structured.ainvoke(messages)
                return {"messages": [AIMessage(content=response_obj.model_dump_json())]}

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

            output = await app.ainvoke(
                {"messages": [{"role": "user", "content": preprocessed_query}]}
            )

            messages = convert_to_messages(output.get("messages", []))
            for msg in reversed(messages):
                if msg.type == "ai" and isinstance(msg.content, str):
                    try:
                        parsed = _json.loads(msg.content)
                        return self._pydantic_object(**parsed).model_dump()
                    except Exception:
                        continue
            raise RuntimeError("call_agent failed: no AI response found")
