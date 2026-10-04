import sys
from pathlib import Path

import streamlit as st

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stPageLink"] a,
        [data-testid="stPageLink"] p {
            font-size: 1.25rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_engineer.data_analytics.pages.fundamental_analytics import (
    render as render_fundamental,
)

# page = st.sidebar.selectbox("Chọn Trang", ["Trang Chủ", "Phân Tích Cơ Bản"])

page = st.sidebar.selectbox("Lựa chọn phân tích", ["Trang Chủ", "Phân Tích Cơ Bản"])

if page == "Trang Chủ":
    st.title("Trang Chủ")

    with st.container():
        st.subheader("💬 Trợ lý AI tài chính")

        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": "Xin chào! Tôi là trợ lý AI phân tích tài chính. Bạn cần hỗ trợ gì hôm nay?"}
            ]

        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        prompt = st.chat_input("Nhập câu hỏi của bạn...")
        if prompt:
            st.session_state["chat_messages"].append({"role": "user", "content": prompt})

            reply = "Đây là phản hồi mẫu cho câu hỏi của bạn."
            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
            st.rerun()

    st.divider()
    st.write("Hoặc lựa chọn các chức năng dưới đây: ")

    st.page_link( "pages/fundamental_analytics.py" ,
        label= "Phân tích cơ bản - Fundamental Analytics" ,
        icon= "📊" ,
    )
    st.write("- Thông tin thị trường đáng chú ý")
    st.write("- Phân tích dự đoán")

elif page == "Phân Tích Cơ Bản":
    render_fundamental()

