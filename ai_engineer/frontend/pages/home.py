import streamlit as st
from ai_engineer.frontend.applications.ai_chatbot.services.session_service import SessionService
from ai_engineer.frontend.state.home_state import (
    initialize_chat_messages,
    initialize_conversation_session,
    initialize_home_session,
)


def render_home():
    initialize_home_session() # Initialize home session - When we start home we will create a new session
    initialize_chat_messages() # Initialize chat messages

    st.title("Trang Chủ")

    with st.container():
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["chat_content"])

        prompt = st.chat_input("Nhập câu hỏi của bạn...")
        if prompt:
            initialize_conversation_session() # When we start conversation we will create a new conversation

            st.session_state["chat_messages"].append({"role": "user", "chat_content": prompt})

            reply = "Đây là phản hồi mẫu cho câu hỏi của bạn."
            st.session_state["chat_messages"].append({"role": "assistant", "chat_content": reply})
            print(st.session_state["chat_messages"])
            st.rerun()

    st.divider()
    st.write("Hoặc lựa chọn các chức năng dưới đây: ")

    st.page_link(
        "pages/fundamental_analytics.py",
        label="Phân tích cơ bản - Fundamental Analytics",
        icon="📊",
    )
    st.write("- Thông tin thị trường đáng chú ý")
    st.write("- Phân tích dự đoán")


if __name__ in {"__main__", "__page__"}:
    render_home()
