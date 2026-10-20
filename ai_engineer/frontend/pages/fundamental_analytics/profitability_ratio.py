import streamlit as st
from ai_engineer.frontend.applications.data_analytics.query.profitability_analytics import (
    operating_margin_query,
    profit_margin_cascade,
    capital_efficiency,
    operating_asset_turnover_query,
    equity_multiplier_query,
    roe_query
)
from ai_engineer.frontend.components.chart.kpi_cart_chart import KpiCardChart
from ai_engineer.frontend.components.chart.line_chart import LineChartComponent
from ai_engineer.frontend.components.chart.table_chart import TableChart
from ai_engineer.frontend.components.markdown.markdown import MarkDown
from ai_engineer.frontend.applications.data_analytics.integrations.db import (
    load_data_from_postgres_polars,
)
import polars as pl

def profitability_ratio():
    df_roe = load_data_from_postgres_polars(roe_query)
    df_roe = df_roe.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

    df_profit_margin = load_data_from_postgres_polars(profit_margin_cascade)
    df_capital_efficiency = load_data_from_postgres_polars(capital_efficiency)
    df_operating_margin = load_data_from_postgres_polars(operating_margin_query)  
    df_operating_margin = df_operating_margin.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )
    # Operating Asset Turnover
    df_operating_asset_turnover = load_data_from_postgres_polars(operating_asset_turnover_query)
    df_operating_asset_turnover = df_operating_asset_turnover.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )
    # Equity Multiplier
    df_equity_multiplier = load_data_from_postgres_polars(equity_multiplier_query)
    df_equity_multiplier = df_equity_multiplier.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

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

    col1, col2, col3 = st.columns(3)
    with col1:
        latest_roa = df_capital_efficiency.row(0, named=True)["roa"]
        KpiCardChart(
            label="Tỷ suất sinh lời trên tổng tài sản - ROA", 
            suffix="%", format="{:.0f}"
            ).render(latest_roa)
    with col2:
        latest_roe = df_capital_efficiency.row(0, named=True)["roe"]
        KpiCardChart(
            label="Tỷ suất sinh lời trên vốn chủ sở hữu - ROE", 
            suffix="%", format="{:.0f}"
        ).render(latest_roe)
    with col3:
        latest_roic = df_capital_efficiency.row(0, named=True)["roic"]
        KpiCardChart(
            label="Tỷ suất sinh lời trên vốn đầu tư - ROIC", 
            suffix="%", format="{:.0f}"
        ).render(latest_roic)
    st.divider()

    # Step 2: Phân tích ROE
    operating_margin_title = MarkDown(
        font_size="24px",    
        text="KHẢ NĂNG SINH LỢI TRÊN VỐN CHỦ SỠ HỮU - ROE (TTM)"
    ).render()

    st.write(
        """
            ROE là một trong những financial ratio được nhà đầu tư quan tâm nhiều nhất

            Theo phương trình DUPONT. ROE gồm 3 thành phần:
            - 1: Biên lợi nhuận ròng: Đo lường khả năng quản lý chi phí và biến doanh thu thành lợi nhuận
            - 2: Vòng quay tài sản: Đo lường hiệu quả quản lý và khai thác tài sản để tạo ra doanh thu
            - 3: Đòn bẩy tài chính: Mức độ doanh nghiệp sử dụng nợ vay để tài trợ cho tài sản.
        """
    )

    operating_margin_title = MarkDown(
        font_size="18px",    
        text="1: Chi tiết các chỉ số cấu tạo nên ROE",
        color="#006b1c",
    ).render()
    TableChart().render(df_roe)

    operating_margin_title = MarkDown(
        font_size="18px",    
        text="2: Thay đổi của ROE theo năm",
        color="#006b1c",
    ).render()
    line_chart = LineChartComponent(
                title="Thay đổi của ROE theo năm",
                x_col="period",
                y_cols=["roe"],
                y_min=25,
                y_max=31,
            )
    line_chart.render(df_roe)

    st.divider()

    # Step 3: Kiểm tra khả năng sinh lợi từ hoạt động kinh doanh cốt lõi
    # EBIT / Doanh thu thuần về bán hàng và cung cấp dịch vụ
    operating_margin_title = MarkDown(
        font_size="24px",    
        text="BIÊN LỢI NHUẬN HOẠT ĐỘNG - Operating Margin"
    ).render()

    st.write(
        """
            Dựa trên tỷ lệ của hai chỉ số sau:
            - 1: Lợi nhuận từ hoạt động kinh doanh cốt lõi
            - 2: Doanh thu thuần về bán hàng và cung cấp dịch vụ
        """
    )

    
    line_chart = LineChartComponent(
                title="Biên lợi nhuận hoạt động",
                x_col="period",
                y_cols=["operating_margin"],
                y_min=0.16,
                y_max=0.2,
            )
    line_chart.render(df_operating_margin)

    st.divider()

    operating_asset_turnover_title = MarkDown(
        font_size="24px",    
        text="VÒNG QUAY TÀI SẢN VẬN HÀNH - Operating Asset Turnover"
    ).render()

    st.write(
        """
            Vòng quay tài sản vân hành đo lường hiệu quả sử dụng các tài sản phục vụ hoạt động kinh doanh cốt lõi
            của doanh nghiệp để tạo ra doanh thu.

            Chỉ số này là tỉ lệ giữa doanh thu thuần (net_revenue) và tài sản vận hành. 
            Trong đó tài sản vận hành là tổng của các loại tài sản sau:
            + Tiền mặt vận hành (Khoảng 2% doanh thu thuần)
            + Các khoản phải thu
            + Hàng tồn kho
            + Tài sản cố định
            + Tài sản dở dang dài hạn
        """
    )

    line_chart = LineChartComponent(
                title="Vòng quay tài sản vân hành",
                x_col="period",
                y_cols=["oat_ratio"],
                y_min=0.6,
                y_max=0.75,
            )
    line_chart.render(df_operating_asset_turnover)
    equity_multiplier_title = MarkDown(
        font_size="24px",    
        text="HỆ SỐ VỐN - Equity Multiplier"
    ).render()

    st.write(
        """
            Hệ số vốn chính là chiến lược cấu trúc vốn: 
            --> Sử dụng nợ vay như thế nào để khuếch đại khả năng sinh lời cho vốn chủ sở hữu.

            Chỉ số này là tỉ lệ giữa TỔNG TÀI SẢN VÀ TỔNG VỐN CHỦ SỠ HỮU
        """
    )

    line_chart = LineChartComponent(
                title="Hệ số vốn",
                x_col="period",
                y_cols=["equity_multiplier"],
                y_min=1.4,
                y_max=1.7,
            )
    line_chart.render(df_equity_multiplier)

    st.divider()
    


if __name__ in {"__main__", "__page__"}:
    profitability_ratio()
