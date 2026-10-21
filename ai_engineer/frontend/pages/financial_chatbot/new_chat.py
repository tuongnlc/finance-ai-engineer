import ast
import json

import streamlit as st
from ai_engineer.frontend.applications.ai_chatbot.services.call_llm.query_understand_service import QueryUnderstandService
from ai_engineer.frontend.applications.ai_chatbot.services.call_llm.chat_with_llm_service import ChatWithLLMService
from ai_engineer.frontend.applications.ai_chatbot.services.message_service import (
    MessageService,
)
from ai_engineer.frontend.state.home_state import (
    initialize_chat_messages,
    initialize_conversation_session,
    initialize_home_session,
    reset_chat,
)
from ai_engineer.helpers.timestamp import create_int_timestamp
from ai_engineer.frontend.applications.ai_chatbot.services.call_llm.tool_calling import ToolCallingService
from ai_engineer.frontend.applications.ai_chatbot.services.response.llm_response_service import (
    LLMResponseService
)



CHAT_INPUT_KEY = "new_chat_prompt"
RERUN_FLAG = "_new_chat_just_rerun_from_message"


def _extract_text_from_tool_output(tool_output) -> str:
    """
    Gom toàn bộ text trong tool_output thành một chuỗi.

    Nội dung tool_output thay đổi theo từng lần gọi tool nên không thể phụ
    thuộc vào key cố định; duyệt đệ quy và lấy mọi giá trị text.
    """
    def _flatten(value) -> list[str]:
        
        if isinstance(value, dict):
            return [text for item in value.values() for text in _flatten(item)]
        
        return [] if value is None else [str(value)]

    texts = []
    for block in tool_output:
        # Block thường có dạng {"type": ..., "text": ..., "id": ...} -> chỉ lấy "text"
        raw = block.get("text", block) if isinstance(block, dict) else block
        texts.extend(_flatten(raw))
    return "\n\n".join(texts)


def render_home():
    # Khi user submit một tin nhắn, giá trị được lưu vào st.session_state[key]
    # ngay từ đầu lần rerun (trước khi st.chat_input được gọi).
    # Dùng nó để phân biệt "navigation mới" với "rerun sau khi gửi tin".
    pending_prompt = st.session_state.get(CHAT_INPUT_KEY)
    just_rerun = st.session_state.pop(RERUN_FLAG, False)

    # Chỉ reset khi là navigation mới (không có prompt đang chờ, không phải rerun sau gửi tin)
    if pending_prompt is None and not just_rerun:
        reset_chat()
        initialize_home_session()
        initialize_chat_messages()

    st.title("Trang Chủ")

    with st.container():
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["chat_content"])

        prompt = st.chat_input("Nhập câu hỏi của bạn...", key=CHAT_INPUT_KEY)
        if prompt:
            initialize_conversation_session() # When we start conversation we will create a new conversation

            st.session_state["chat_messages"].append({"role": "user", "chat_content": prompt})

            # Write message (prompt) to backend
            created_message = MessageService().create_message(
                conversation_id=st.session_state["conversation_id"],
                user_id=st.session_state["user_id"],
                created_timestamp=create_int_timestamp(),
                content=prompt,
            )

            # Query understanding
            with st.spinner("AI đang suy nghĩ..."):
                query_understand_result = QueryUnderstandService().query_understand(
                    content=prompt,
                    question_context=prompt,
                )

                reply = json.loads(query_understand_result.response)

                #Implement tool calling ToolCallingService
                tool_calling_output = ToolCallingService().tool_calling(
                    original_query=prompt,
                    vietnamese_with_diacritics=prompt,
                    question_type=reply["question_type"],
                    main_topic=reply["main_topic"],
                    stock_id=reply["stock_id"],
                    target_year=reply["target_year"],
                    document_type=reply["document_type"],
                    optimized_search_query=", ".join(reply["optimized_search_query"]),
                )

                tool_output = ast.literal_eval(tool_calling_output.tool_output)
                print(tool_output)

                # Get text from tool_output and use as question context
                question_context = _extract_text_from_tool_output(tool_output)

                # Sending to ai to get response
                chat_with_llm_output = ChatWithLLMService().chat_with_llm(
                    content=prompt,
                    question_context=question_context,
                )

                llm_response = chat_with_llm_output.response
                # Save response to database
                LLMResponseService().create_llm_response(
                    message_id=created_message.id,
                    conversation_id=st.session_state["conversation_id"],
                    llm_response=llm_response,
                    content_type="text",
                )

                        
            st.session_state["chat_messages"].append({"role": "assistant", "chat_content": llm_response})
            print(st.session_state["chat_messages"])
            st.session_state[RERUN_FLAG] = True
            st.rerun()

    st.divider()

if __name__ in {"__main__", "__page__"}:
    render_home()
