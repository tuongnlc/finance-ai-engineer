import operator
import asyncio
import sys
import warnings
import logging
from pathlib import Path
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage, ToolMessage, convert_to_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv
import os
import mlflow
import requests

from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

warnings.filterwarnings("ignore", message="Key 'additionalProperties' is not supported in schema, ignoring")
logging.getLogger().addFilter(lambda r: "additionalProperties" not in r.getMessage())

_w = sys.stdout.write
sys.stdout.write = lambda s, _orig=_w: _orig(s) if "additionalProperties" not in s else None
_e = sys.stderr.write
sys.stderr.write = lambda s, _orig=_e: _orig(s) if "additionalProperties" not in s else None

mlflow.langchain.autolog()
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("tracing_agent_new")


prompt_template = [
    {
        "role": "system",
        "content": (
            "Role: Bạn là bộ suy luận của AI Agent cho hệ thống chatbot tài chính. "
            "Nhiệm vụ của bạn là đọc nội dung đầu vào dạng JSON và gọi chính xác 1 tool phù hợp. "
            "\n"
            "---\n"
            "\n"
            "### QUY TẮC BẮT BUỘC:\n"
            "1. Dựa trên `question_type` trong input để chọn tool:\n"
            "   - question_type là 'tin tức thị trường' → gọi tool `get_news_from_db`\n"
            "   - question_type là 'tin tức doanh nghiệp' → gọi tool `get_news_from_db`\n"
            "   - question_type là 'tài chính doanh nghiệp' → gọi tool `get_financial_data`\n"
            "   - question_type là 'câu hỏi không liên quan' → gọi tool `search_internet`\n"
            "2. Đọc kỹ SCHEMA (tham số) của tool đã chọn, CHỈ truyền những tham số mà tool định nghĩa, đúng tên field và đúng kiểu dữ liệu. Tuyệt đối không tự thêm tham số tool không có.\n"
            "Ví dụ nếu tool định nghĩa tham số là stock_id thì truyền args là stock_id. \n"
            "Ví dụ nếu tool định nghĩa tham số là query và stock_id thì truyền args là query và stock_id. \n"
            "3. Gọi tool đã chọn. Đợi tool hoàn thành và ghi nhớ kết quả.\n"
            "4. Trả về kết quả dưới dạng sau: " 
            "{{"
                '"tool_output": "Hello! Welcome to your local MCP server",'
                '"tool_name": "get_greeting",'
                '"input_message": {input}'
            "}}"  
        ),
    },
    {
        "role": "user",
        "content": (
            "Nội dung đầu vào: {input}\n"
            "Gọi tool phù hợp với dữ liệu trên, đúng schema tham số của tool."
        ),
    },
]

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
        return str(data.get("response", data))
    else:
        raise RuntimeError(f"query_transformation failed: {response.status_code}")
    

async def call_agent(preprocessed_query: str):
    async with MCPAdapter("http://127.0.0.1:7000/sse") as adapter:
        tools, tool_map = await _connect_tool(adapter)

        model_with_tools = model.bind_tools(tools)

        async def call_model(state: AgentState):
            msgs = convert_to_messages(state["messages"])
            user_msg = [m for m in msgs if m.type == "human"][-1]
            messages = ChatPromptTemplate.from_messages(prompt_template).format_messages(input=user_msg.content)
            messages += [m for m in msgs if m.type != "human"]

            print("Here is message: ")
            print(messages)

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
        print("Here is output")
        print(output)
        print("")
        # return output

        #extract final output
        messages = output.get("messages", [])
        for msg in reversed(messages):
            msg_type = getattr(msg, "type", None) or (isinstance(msg, dict) and msg.get("role"))
            if msg_type == "ai":
                content = msg.content if hasattr(msg, "content") else (isinstance(msg, dict) and msg.get("content", ""))
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            print("--- Text Content ---")
                            return block["text"]
                else:
                    raise RuntimeError(f"call_agent failed: {content}")

async def main():
    content = "Ngan Hang ACB"
    preprocessed_query = await query_transformation(content)
    response = await call_agent(preprocessed_query)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
