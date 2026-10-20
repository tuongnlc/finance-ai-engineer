import streamlit as st
from ai_engineer.frontend.applications.data_analytics.query.debt_management_analytics import (
    capital_structure,
    interest_cover,
    operating_cash_flow_to_total_debt
)
from ai_engineer.frontend.components.chart.kpi_cart_chart import KpiCardChart
from ai_engineer.frontend.components.markdown.markdown import MarkDown
from ai_engineer.frontend.applications.data_analytics.integrations.db import load_data_from_postgres_polars
import polars as pl
from ai_engineer.frontend.components.chart.line_chart import LineChartComponent


def debt_management_ratio():
    df_capital_structure = load_data_from_postgres_polars(capital_structure)
    df_capital_structure = df_capital_structure.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

    df_interest_cover = load_data_from_postgres_polars(interest_cover)
    df_interest_cover = df_interest_cover.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

    df_ocf_to_total_debt = load_data_from_postgres_polars(operating_cash_flow_to_total_debt)
    df_ocf_to_total_debt = df_ocf_to_total_debt.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

    st.set_page_config(
        page_title="Debt Management Ratio",
        layout="wide"  
    )

    title = MarkDown(
        font_size="30px",    
        text="PHÂN TÍCH KHẢ NĂNG QUẢN TRỊ NỢ"
    ).render()

    st.write(
        """
            Trong báo cáo này, chúng ta sẽ phân tích khả năng quản trị nợ của công ty.
            + Tỉ lệ giữa nợ và tổng tài sản và nợ trên vốn
            + Khả năng chi trả lãi vay của doanh nghiệp
            + Khả năng thanh toán nợ của doanh nghiệp
        """
    )
    st.divider()

    # Step 1: Visualize main kpi
    main_kpt = MarkDown(
        font_size="24px",    
        text="CÁC CHỈ SỐ CƠ BẢN"
    ).render()

    col1, col2, col3 = st.columns(3)
    with col1:
        latest_current_assets = df_capital_structure.row(0, named=True)["total_assets"]
        KpiCardChart(
            label="Tổng tài sản", 
            suffix="", format="{:.0f}"
            ).render(latest_current_assets)
    with col2:
        latest_current_assets = df_capital_structure.row(0, named=True)["total_liabilities"]
        KpiCardChart(
            label="Tổng nợ", 
            suffix="", format="{:.0f}"
            ).render(latest_current_assets)
    with col3:
        latest_current_assets = df_capital_structure.row(0, named=True)["total_equity"]
        KpiCardChart(
            label="Tổng vốn", 
            suffix="", format="{:.0f}"
            ).render(latest_current_assets)

    col1, col2 = st.columns(2)
    with col1:
        latest_icr = df_interest_cover.row(0, named=True)["icr"]
        KpiCardChart(
            label="Interest Cover Ratio - ICR", 
            suffix="", format="{:.2f}"
            ).render(latest_icr)
    with col2:
        latest_icr = df_ocf_to_total_debt.row(0, named=True)["ocf_to_total_debt_ttm"]
        KpiCardChart(
            label="Operating Cash Flow-to-Total Debt Ratio", 
            suffix="", format="{:.2f}"
            ).render(latest_icr)

    st.divider()

    # Step 2: Capital structure
    main_kpt = MarkDown(
        font_size="24px",    
        text="CẤU TRÚC NGUỒN VỐN"
    ).render()

    st.write(
        """
            Cấu trúc nguồn vốn (hay Cơ cấu nguồn vốn, tiếng Anh là Capital Structure) 
            đại diện cho tỷ lệ phối hợp giữa các nguồn tài chính khác nhau mà doanh nghiệp 
            huy động để tài trợ cho tài sản và hoạt động kinh doanh của doanh nghiệp.
        """
    )

    line_chart = LineChartComponent(
                title="1: Tỉ lệ nợ trên tài sản",
                x_col="period",
                y_cols=["debt_to_asset"],
                y_min=0.3,
                y_max=0.4,
            )
    line_chart.render(df_capital_structure)

    line_chart = LineChartComponent(
                title="2:Tỉ lệ nợ trên vốn",
                x_col="period",
                y_cols=["debt_to_equity"],
                y_min=0.45,
                y_max=0.65,
            )
    line_chart.render(df_capital_structure)

    st.divider()

    # Step 3: Interest cover ratio
    main_kpt = MarkDown(
        font_size="24px",    
        text="KHẢ NĂNG THANH TOÁN LÃI VAY"
    ).render()

    st.write(
        """
            Khả năng thanh toán lãi vay (tiếng Anh: Interest Coverage Ratio - ICR) 
            đại diện cho năng lực tạo ra lợi nhuận của doanh nghiệp để trang chi trả cho các khoản chi phí lãi vay phát sinh trong kỳ.
        """
    )

    line_chart = LineChartComponent(
                title="Khả năng thanh toán lãi vay",
                x_col="period",
                y_cols=["icr"],
                y_min=20,
                y_max=41,
            )
    line_chart.render(df_interest_cover)

    st.divider()
    # Step 4: Operating cash flow-to-total debt ratio
    main_kpt = MarkDown(
        font_size="24px",    
        text="DÒNG TIỀN VẬN HÀNH TRÊN TỔNG NỢ"
    ).render()

    st.write(
        """
            Chỉ số Dòng tiền vận hành trên Tổng nợ (tiếng Anh: Operating Cash Flow-to-Total Debt Ratio - OCF/Total Debt) đại diện cho năng lực 
            trả toàn bộ nợ bằng tiền mặt thực tế của doanh nghiệp dựa trên hoạt động kinh doanh cốt lõi trong kỳ.
        """
    )

    line_chart = LineChartComponent(
        title="Dòng tiền vận hành trên tổng nợ",
        x_col="period",
        y_cols=["ocf_to_total_debt_ttm"],
        y_min=0.35,
        y_max=0.5,
    )
    line_chart.render(df_ocf_to_total_debt)

if __name__ == "__main__":
    debt_management_ratio()