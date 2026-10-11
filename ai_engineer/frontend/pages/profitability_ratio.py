import streamlit as st
from ai_engineer.frontend.applications.data_analytics.query.profitability_analytics import profit_margin_cascade
from ai_engineer.frontend.components.chart.kpi_cart_chart import KpiCardChart
from ai_engineer.frontend.components.markdown.markdown import MarkDown
from ai_engineer.frontend.applications.data_analytics.integrations.db import load_data_from_postgres_polars

def profitability_ratio():
    #Prepare data
    df_profit_margin = load_data_from_postgres_polars(profit_margin_cascade)



    st.set_page_config(
        page_title="Profitability Ratio",
        layout="wide"  
    )
    title = MarkDown(
        font_size="30px",    
        text="PHÂN TÍCH KHẢ NĂNG SINH LỢI"
    ).render()

    st.write(
        """
            Trong báo cáo này, chúng ta sẽ phân tích cách công ty sử dụng vốn và nợ 
            như thế nào để tạo ra doanh thu và lợi nhuận. 

            Tập trung vào hoạt động kinh doanh cốt lõi của công ty            
            - 1: Doanh thu
            - 2: Lợi nhuận
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
        latest_net_revenue = df_profit_margin.row(0, named=True)["net_revenue"]
        KpiCardChart(
            label="Doanh thu thuần về bán hàng<br>và cung cấp dịch vụ", 
            suffix="", format="{:.0f}"
            ).render(latest_net_revenue)
    with col2:
        latest_profit_margin = df_profit_margin.row(0, named=True)["gross_profit"]
        KpiCardChart(
            label="Lợi nhuận gộp về bán hàng và cung cấp dịch vụ", 
            suffix="", format="{:.0f}"
            ).render(latest_profit_margin)
    with col3:
        latest_net_operating_profit = df_profit_margin.row(0, named=True)["net_operating_profit"]
        KpiCardChart(
            label="Lợi nhuận thuần từ hoạt động kinh doanh", 
            suffix="", format="{:.0f}"
            ).render(latest_net_operating_profit)


if __name__ in {"__main__", "__page__"}:
    profitability_ratio()
