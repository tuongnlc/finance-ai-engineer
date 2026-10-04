import pandas as pd
import streamlit as st

from ai_engineer.data_analytics.components.chart.table_chart import TableChart
from ai_engineer.data_analytics.components.chart.line_chart import LineChartComponent
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


def fundamental_analytics():
    st.title("Phân Tích Cơ Bản")

    st.sidebar.selectbox("Lựa chọn doanh nghiệp để phân tích", 
        [
            "VNM", 
            "ACB"
        ]
    )

    st.divider()

    vnm_df_pl = load_data_from_postgres_polars(VNM_REVENUE_QUERY)
    vnm_df = vnm_df_pl.to_pandas()

    if not vnm_df.empty:
        vnm_df["period"] = vnm_df["year"].astype(str) + " Q" + vnm_df["quarter"].astype(str)

        st.write("Phân tích khả năng sinh lợi")

        table_vnm = TableChart(title="Doanh Thu Gộp VNM")
        table_vnm.render(vnm_df[["period", "gross_revenue"]])

        chart = LineChartComponent(
            title="Xu Hướng Doanh Thu Gộp VNM",
            x_col="period",
            y_col="gross_revenue",
        )
        chart.render(vnm_df)
    else:
        st.info("Không có dữ liệu doanh thu VNM từ CSDL.")


if __name__ in {"__main__", "__page__"}:
    fundamental_analytics()
