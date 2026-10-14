
import uuid

import streamlit as st
from ai_engineer.frontend.applications.ai_chatbot.services.conversation_service import (
    ConversationService,
)
from ai_engineer.frontend.applications.ai_chatbot.services.session_service import SessionService


WELCOME_MESSAGE = {
    "role": "assistant",
    "chat_content": "Xin chào! Tôi là trợ lý AI phân tích tài chính. Bạn cần hỗ trợ gì hôm nay?",
}
import random

def initialize_home_session() -> None:
    if st.session_state.get("home_session_initialized"):
        return

    session_context = SessionService().start_new_session()
    st.session_state["session_id"] = str(session_context.session_id)
    st.session_state["conversation_id"] = None
    st.session_state["home_session_initialized"] = True
    st.session_state["user_id"] = random.choice(["tuong_nlc", "tuong_nlc_1", "tuong_nlc_2", "tuong_nlc_3", "tuong_nlc_4", "tuong_nlc_5"])

def initialize_chat_messages() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [WELCOME_MESSAGE]


def initialize_conversation_session() -> None:
    if st.session_state.get("conversation_session_initialized"):
        return

    session_id_str = st.session_state.get("session_id")
    conversation_id_str = st.session_state.get("conversation_id")

    conversation_context = ConversationService().start_new_conversation(
        session_id=uuid.UUID(session_id_str),
        user_id=random.choice(["tuong_nlc", "tuong_nlc_1", "tuong_nlc_2", "tuong_nlc_3", "tuong_nlc_4", "tuong_nlc_5"]),

        conversation_id=(
            uuid.UUID(conversation_id_str) if conversation_id_str else None
        ),
        context={"home_page_opened": True},
    )

    st.session_state["conversation_id"] = str(conversation_context.conversation_id)
    st.session_state["conversation_context"] = conversation_context
    st.session_state["conversation_session_initialized"] = True


def reset_chat() -> None:
    """Xóa lịch sử chat hiện tại và chuẩn bị cho một cuộc trò chuyện mới."""
    st.session_state["chat_messages"] = [WELCOME_MESSAGE]
    st.session_state["conversation_id"] = None
    st.session_state["conversation_session_initialized"] = False
    st.session_state.pop("conversation_context", None)
    st.session_state["home_session_initialized"] = False
    st.session_state["session_id"] = None
