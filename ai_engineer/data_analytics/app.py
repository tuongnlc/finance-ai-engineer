import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

fundamental_page = st.Page(
    "pages/fundamental_analytics.py",
    title="Phân Tích Cơ Bản",
    icon="📊",
)

home_page = st.Page(
    "pages/home.py",
    title="Trang Chủ",
    icon="🏠",
    default=True,
)

pg = st.navigation({
    "Chức năng chính": [home_page, fundamental_page],
}, position="sidebar")

pg.run()
