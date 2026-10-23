import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_engineer.frontend.state.home_state import reset_chat

# CHATBOT PAGE
home_page = st.Page(
    "pages/financial_chatbot/new_chat.py",
    title="Đoạn trò chuyện mới",
    icon="🏠",
    default=True,
)

historical_chat = st.Page(
    "pages/financial_chatbot/historical_chat.py",
    title="Lịch sử trò chuyện",
    icon="🏠",
)

# FUNDAMENTAL ANALYSIS PAGE
fundamental_page = st.Page(
    "pages/fundamental_analytics/fundamental_analytics.py",
    title="Tổng quan chỉ số",
    icon="📊",
)

profitability_ratio_page = st.Page(
    "pages/fundamental_analytics/profitability_ratio.py",
    title="Khả năng sinh lợi",
    icon="📊",
)

liquidity_ratio_page = st.Page(
    "pages/fundamental_analytics/liquidity_ratio.py",
    title="Chỉ số thanh khoản",
    icon="📊",
)

debt_management_ratio_page = st.Page(
    "pages/fundamental_analytics/debt_management_ratio.py",
    title="Khả năng quản trị nợ",
    icon="📊",
)

# TECHNICAL ANALYSIS PAGE

# MARKET INFO PAGE
market_news_page = st.Page(
    "pages/market_info/market_news.py",
    title="Tin tức thị trường",
    icon="📰",
)

favorite_news_page = st.Page(
    "pages/market_info/favorite_news.py",
    title="Tin tức đáng chú ý",
    icon="📰",
)

# IMAGE RENDER PAGE
img_render_page = st.Page(
    "pages/img_render/img_render.py",
    title="Render ảnh",
    icon="🖼",
    default=False,
)


# RENDER PAGE
pg = st.navigation({
    "Chatbot tài chính": [home_page, historical_chat],
    "CHỨNG KHOÁN - PHÂN TÍCH CƠ BẢN": [
        fundamental_page, 
        profitability_ratio_page, 
        liquidity_ratio_page, 
        debt_management_ratio_page
    ],
    "CHỨNG KHOÁN - PHÂN TÍCH KỸ THUẬT": [],
    "THÔNG TIN KINH TẾ": [
        market_news_page,
        favorite_news_page,
    ],
    "BẤT ĐỘNG SẢN": [],
    "VÀNG": [],
    "Render ảnh": [img_render_page],
}, position="sidebar")

pg.run()
