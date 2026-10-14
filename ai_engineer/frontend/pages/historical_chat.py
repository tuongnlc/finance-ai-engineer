import streamlit as st
from ai_engineer.frontend.applications.ai_chatbot.services.session_service import SessionService
# from ai_engineer.frontend.state.home_state import ()


def render_home():
    st.title("Lịch sử trò chuyện")


if __name__ in {"__main__", "__page__"}:
    render_home()
