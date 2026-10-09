
import streamlit as st
from ai_engineer.ai_chatbot.services.session_service import SessionService

WELCOME_MESSAGE = {
    "role": "assistant",
    "chat_content": "Xin chào! Tôi là trợ lý AI phân tích tài chính. Bạn cần hỗ trợ gì hôm nay?",
}


def initialize_home_session() -> None:
    if st.session_state.get("home_session_initialized"):
        return

    session_context = SessionService().start_new_session()
    st.session_state["session_id"] = str(session_context.session_id)
    st.session_state["conversation_id"] = str(session_context.conversation_id)
    st.session_state["home_session_initialized"] = True


def initialize_chat_messages() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [WELCOME_MESSAGE]
