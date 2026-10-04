import streamlit as st


def render_home():
    st.title("Trang Chủ")

    with st.container():
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

    st.page_link(
        "pages/fundamental_analytics.py",
        label="Phân tích cơ bản - Fundamental Analytics",
        icon="📊",
    )
    st.write("- Thông tin thị trường đáng chú ý")
    st.write("- Phân tích dự đoán")


if __name__ in {"__main__", "__page__"}:
    render_home()
