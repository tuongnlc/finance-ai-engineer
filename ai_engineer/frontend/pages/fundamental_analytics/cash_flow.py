import streamlit as st

from ai_engineer.frontend.components.chart.kpi_cart_chart import KpiCardChart
from ai_engineer.frontend.components.markdown.markdown import MarkDown
from ai_engineer.frontend.applications.data_analytics.integrations.db import (
    load_data_from_postgres_polars,
)
from ai_engineer.frontend.applications.data_analytics.query.cash_flow_analytics import (
    kpi_increase_query,
)


def cash_flow():
    #Repair data
    df = load_data_from_postgres_polars(kpi_increase_query)

    st.set_page_config(
        page_title="Cash Flow Analytics",
        layout="wide"  
    )

    title = MarkDown(
        font_size="30px",    
        text="PHÂN TÍCH DÒNG TIỀN"
    ).render()

    st.write(
        """
            Trong báo cáo này, chúng ta sẽ phân tích dòng tiền hiện tại của công ty
            + 1: Doanh thu thuần
            + 2: Lơi nhuận sau thuế
            + 3: Lợi nhuận trước thuế và lãi vay
            + 4: Lợi nhuận trước thuế, lãi vay và hao mòn
            + 5: Dòng tiền từ hoạt động kinh doanh
            + 6: Dòng tiền tự do
        """
    )
    st.divider()

    #Step 1: Main kpi
    main_kpi = MarkDown(
        font_size="24px",    
        text="CÁC CHỈ SỐ CƠ BẢN"
    ).render()

    ## Các chỉ số cơ bản
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        latest_revenue = df.row(0, named=True)["net_revenue"]
        KpiCardChart(
            label="Doanh thu thuần", 
            suffix="", format="{:.0f}"
            ).render(latest_revenue)
    with col2:
        latest_profit = df.row(0, named=True)["net_profit_after_corporate_income_tax"]
        KpiCardChart(
            label="Lợi nhuận sau thuế", 
            suffix="", format="{:.0f}"
            ).render(latest_profit)
    with col3:
        latest_profit_before_corporate_income_tax = df.row(0, named=True)["ebit"]
        KpiCardChart(
            label="Lợi nhuận trước thuế và lãi vay", 
            suffix="", format="{:.0f}"
            ).render(latest_profit_before_corporate_income_tax)
    with col4:
        latest_profit_before_corporate_income_tax_and_interest = df.row(0, named=True)["ebitda"]
        KpiCardChart(
            label="Lợi nhuận trước thuế, lãi vay và hao mòn", 
            suffix="", format="{:.0f}"
            ).render(latest_profit_before_corporate_income_tax_and_interest)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        latest_revenue = df.row(0, named=True)["revenue_growth_yoy_pct"]
        KpiCardChart(
            label="Tăng trưởng doanh thu YoY (%)", 
            suffix="", format="{:.0f}"
            ).render(latest_revenue)
    with col2:
        latest_profit = df.row(0, named=True)["net_profit_growth_yoy_pct"]
        KpiCardChart(
            label="Tăng trưởng lợi nhuận sau thuế YoY (%)", 
            suffix="", format="{:.0f}"
            ).render(latest_profit)
    with col3:
        latest_profit_before_corporate_income_tax = df.row(0, named=True)["ebit_growth_yoy_pct"]
        KpiCardChart(
            label="Tăng trưởng lợi nhuận trước thuế và lãi vay YoY (%)", 
            suffix="", format="{:.0f}"
            ).render(latest_profit_before_corporate_income_tax)
    with col4:
        latest_profit_before_corporate_income_tax_and_interest = df.row(0, named=True)["ebitda_growth_yoy_pct"]
        KpiCardChart(
            label="Tăng trưởng lợi nhuận trước thuế, lãi vay và hao mòn YoY (%)", 
            suffix="", format="{:.0f}"
            ).render(latest_profit_before_corporate_income_tax_and_interest)

    st.markdown("...")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        latest_ocf = df.row(0, named=True)["ocf"]
        KpiCardChart(
            label="Dòng tiền từ hoạt động kinh doanh", 
            suffix="", format="{:.0f}"
            ).render(latest_ocf)
    with col2:
        latest_fcff = df.row(0, named=True)["fcff"]
        KpiCardChart(
            label="Dòng tiền tự do", 
            suffix="", format="{:.0f}"
            ).render(latest_fcff)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        latest_ocf = df.row(0, named=True)["ocf_growth_yoy_pct"]
        KpiCardChart(
            label="Thay đổi trong dòng tiền từ hoạt động kinh doanh YoY (%)", 
            suffix="", format="{:.0f}"
            ).render(latest_ocf)
    with col2:
        latest_fcff = df.row(0, named=True)["fcff_growth_yoy_pct"]
        KpiCardChart(
            label="Thay đổi trong dòng tiền tự do YoY (%)", 
            suffix="", format="{:.0f}"
            ).render(latest_fcff)

    st.divider()
    main_kpi = MarkDown(
        font_size="24px",    
        text="TĂNG TRƯỞNG THEO QUÝ"
    ).render()

    st.write("Chưa đủ số liệu đẻ làm cái này")

if __name__ == "__main__":
    cash_flow()
