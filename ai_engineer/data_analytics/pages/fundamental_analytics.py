import pandas as pd
import streamlit as st

from ai_engineer.data_analytics.components.table_chart import TableChart


def render():
    st.title("Phân Tích Cơ Bản")

    data = pd.DataFrame(
        {
            "Mã CK": ["TCB", "MBB", "VCB", "BID", "STB"],
            "P/E": [8.5, 7.2, 10.1, 9.3, 6.8],
            "P/B": [1.2, 1.0, 1.8, 1.5, 0.9],
            "ROE (%)": [22.3, 19.5, 25.1, 21.0, 18.2],
            "EPS (VND)": [3200, 2800, 4500, 3900, 2100],
        }
    )

    table = TableChart(title="Chỉ Số Cơ Bản Ngân Hàng")
    table.render(data)