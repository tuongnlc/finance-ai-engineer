import random
import streamlit as st
from ai_engineer.frontend.applications.ai_chatbot.services.conversation_service import (
    ConversationService,
)


def render_home():
    st.title("Lịch sử trò chuyện")

    user_id = random.choice(
        ["tuong_nlc", "tuong_nlc_1", "tuong_nlc_2", "tuong_nlc_3", "tuong_nlc_4", "tuong_nlc_5"]
    )
    st.caption(f"User: {user_id}")

    service = ConversationService()

    try:
        conversations = service.list_conversations(user_id=user_id)
    except Exception as exc:
        st.error(f"Không thể lấy danh sách hội thoại: {exc}")
        return

    if not conversations:
        st.info("Chưa có hội thoại nào.")
        return

    for conv in conversations:
        with st.container(border=True):
            st.caption(conv.title or "(Không tiêu đề)")

if __name__ in {"__main__", "__page__"}:
    render_home()
