import operator
import asyncio
import sys
import json
from pathlib import Path
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, convert_to_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv
import os
import mlflow

mlflow.langchain.autolog()
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("tracing_agent")


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
    # max_retries=5,
)

async def _connect_tool(adapter: MCPAdapter):
    all_tools = await adapter.list_tools()
    tool_map = {t.name: t for t in all_tools}
    return all_tools, tool_map

async def main():
    async with MCPAdapter("http://127.0.0.1:8000/sse") as adapter:
        tools, tool_map = await _connect_tool(adapter)

        model_with_tools = model.bind_tools(tools)

        async def call_model(state: AgentState):
            msgs = convert_to_messages(state["messages"])
            user_msg = [m for m in msgs if m.type == "human"][-1]
            messages = ChatPromptTemplate.from_messages(prompt_template).format_messages(input=user_msg.content)
            messages += [m for m in msgs if m.type != "human"]
            response = await model_with_tools.ainvoke(messages)
            for tc in response.tool_calls:
                print(f"[LOG] Model emit tool_call: name={tc['name']} args={tc['args']}")
            return {"messages": [response]}

        async def call_tools(state: AgentState):
            messages = convert_to_messages(state["messages"])
            last_message = messages[-1]

            tool_messages = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_to_invoke = tool_map[tool_name]

                print(f"[LOG] Invoking tool: name={tool_name} args={tool_args}")
                tool_output = await tool_to_invoke.ainvoke(tool_args)
                print(f"[LOG] Tool output: name={tool_name} output={tool_output}")

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

        input_data = {'original_query': 'Loi nhuan cua ngan hang ACB ngay 10 thang 9', 'vietnamese_with_diacritics': 'Lợi nhuận của ngân hàng ACB ngày 10 tháng 9', 'question_type': 'tài chính doanh nghiệp', 'main_topic': 'Tài chính Doanh nghiệp', 'stock_id': 'ACB', 'target_year': '2026', 'document_type': 'income_statement', 'optimized_search_query': ['báo cáo lợi nhuận ngân hàng ACB năm 2026', 'tình hình tài chính và lợi nhuận ACB mới nhất', 'số liệu doanh thu lợi nhuận ngân hàng ACB năm 2026']}
        output = await app.ainvoke({"messages": [{"role": "user", "content": json.dumps(input_data, ensure_ascii=False)}]})

        # for message in output["messages"]:
            # print(message)
            


if __name__ == "__main__":
    asyncio.run(main())
