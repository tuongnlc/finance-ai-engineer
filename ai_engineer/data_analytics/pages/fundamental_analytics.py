import pandas as pd
import streamlit as st

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

from ai_engineer.data_analytics.components.table_chart import TableChart
from ai_engineer.data_analytics.components.line_chart import LineChartComponent
from ai_engineer.data_analytics.infrastructure.db import load_data_from_postgres_polars

VNM_REVENUE_QUERY = """
        SELECT 
            year,
            quarter,
            gross_revenue
        FROM public.fs_income_statement_type_one
        WHERE stock_id = 'VNM'
        ORDER BY year, quarter
    """


def render():
    st.title("Phân Tích Cơ Bản")

    # data = pd.DataFrame(
    #     {
    #         "Mã CK": ["TCB", "MBB", "VCB", "BID", "STB"],
    #         "P/E": [8.5, 7.2, 10.1, 9.3, 6.8],
    #         "P/B": [1.2, 1.0, 1.8, 1.5, 0.9],
    #         "ROE (%)": [22.3, 19.5, 25.1, 21.0, 18.2],
    #         "EPS (VND)": [3200, 2800, 4500, 3900, 2100],
    #     }
    # )

    # table = TableChart(title="Chỉ Số Cơ Bản Ngân Hàng")
    # table.render(data)

    st.divider()

    vnm_df_pl = load_data_from_postgres_polars(VNM_REVENUE_QUERY)
    vnm_df = vnm_df_pl.to_pandas()

    if not vnm_df.empty:
        vnm_df["period"] = vnm_df["year"].astype(str) + " Q" + vnm_df["quarter"].astype(str)

        table_vnm = TableChart(title="Doanh Thu Gộp VNM (từ DB)")
        table_vnm.render(vnm_df[["period", "gross_revenue"]])

        chart = LineChartComponent(
            title="Xu Hướng Doanh Thu Gộp VNM",
            x_col="period",
            y_col="gross_revenue",
        )
        chart.render(vnm_df)
    else:
        st.info("Không có dữ liệu doanh thu VNM từ CSDL.")

render()
