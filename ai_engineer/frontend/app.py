import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_engineer.frontend.state.home_state import reset_chat

# CHATBOT PAGE
home_page = st.Page(
    "pages/new_chat.py",
    title="Đoạn trò chuyện mới",
    icon="🏠",
    default=True,
)

historical_chat = st.Page(
    "pages/historical_chat.py",
    title="Lịch sử trò chuyện",
    icon="🏠",
)

# FUNDAMENTAL ANALYSIS PAGE
fundamental_page = st.Page(
    "pages/fundamental_analytics.py",
    title="Tổng quan chỉ số",
    icon="📊",
)

profitability_ratio_page = st.Page(
    "pages/profitability_ratio.py",
    title="Khả năng sinh lợi",
    icon="📊",
)

# IMAGE RENDER PAGE
img_render_page = st.Page(
    "pages/img_render.py",
    title="Render ảnh",
    icon="🖼",
    default=False,
)


# RENDER PAGE
pg = st.navigation({
    "Chatbot tài chính": [home_page, historical_chat],
    "PHÂN TÍCH CƠ BẢN": [fundamental_page, profitability_ratio_page,],
    "Phân tích kỹ thuật": [],
    "Render ảnh": [img_render_page],
}, position="sidebar")

pg.run()
