import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_engineer.data_analytics.pages.fundamental_analytics import (
    render as render_fundamental,
)

# page = st.sidebar.selectbox("Chọn Trang", ["Trang Chủ", "Phân Tích Cơ Bản"])
page = st.sidebar.radio("Chọn Trang", ["Trang Chủ", "Phân Tích Cơ Bản"])

if page == "Trang Chủ":
    st.title("Trang Chủ Dashboard")
elif page == "Phân Tích Cơ Bản":
    render_fundamental()

