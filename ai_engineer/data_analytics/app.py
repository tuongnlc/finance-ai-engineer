import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# CHATBOT PAGE
home_page = st.Page(
    "pages/home.py",
    title="AI chatbot",
    icon="🏠",
    default=True,
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



pg = st.navigation({
    "Chatbot tài chính": [home_page],
    "PHÂN TÍCH CƠ BẢN": [fundamental_page, profitability_ratio_page,],
    "Phân tích kỹ thuật": [],
}, position="sidebar")

pg.run()
