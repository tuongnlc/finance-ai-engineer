import streamlit as st
import polars as pl
from ai_engineer.frontend.components.chart.kpi_cart_chart import KpiCardChart
from ai_engineer.frontend.components.chart.line_chart import LineChartComponent
from ai_engineer.frontend.components.markdown.markdown import MarkDown
from ai_engineer.frontend.applications.data_analytics.query.liquidity_analytics import (
    days_inventory_outstanding_query,
    short_term_solvency_ratios_query,
    days_sales_outstanding_query
)
from ai_engineer.frontend.applications.data_analytics.integrations.db import (
    load_data_from_postgres_polars,
)

def liquidity_ratio():
    #Repaird data
    df_short_term_solvency_ratios = load_data_from_postgres_polars(short_term_solvency_ratios_query)
    df_short_term_solvency_ratios = df_short_term_solvency_ratios.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )
    # Days Inventory Outstanding
    df_days_inventory_outstanding = load_data_from_postgres_polars(days_inventory_outstanding_query)
    df_days_inventory_outstanding = df_days_inventory_outstanding.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

    # Days Sales Outstanding
    df_days_sales_outstanding = load_data_from_postgres_polars(days_sales_outstanding_query)
    df_days_sales_outstanding = df_days_sales_outstanding.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )

    # Join 2 df above to calculate Operating Cycle - Chu kỳ hoạt động
    df_operating_cycle = df_days_inventory_outstanding.join(
        df_days_sales_outstanding,
        on=["period", "stock_id"],
        how="full"
    )
    df_operating_cycle = df_operating_cycle.with_columns(
        operation_cycle = pl.col("days_inventory_outstanding").cast(pl.Int16) + pl.col("days_sales_outstanding").cast(pl.Int16)
    ).select(["period", "stock_id", "operation_cycle"])
    df_operating_cycle.show()


    st.set_page_config(
        page_title="Liquidity Ratio",
        layout="wide"  
    )

    title = MarkDown(
        font_size="30px",    
        text="PHÂN TÍCH CHỈ SỐ THANH KHOẢN"
    ).render()

    st.write(
        """
            Trong báo cáo này, chúng ta sẽ phân tích khả năng hoạt động liên tục của công ty.
            + Khả năng chi trả lãi vay 
            + Chu kỳ hoạt động kinh doanh của doanh nghiệp
        """
    )

    st.divider()
    #Step 1: Main kpi
    main_kpt = MarkDown(
        font_size="24px",    
        text="CÁC CHỈ SỐ CƠ BẢN"
    ).render()

    ## Các chỉ số chính
    col1, col2, col3 = st.columns(3)
    with col1:
        latest_current_assets = df_short_term_solvency_ratios.row(0, named=True)["current_assets"]
        KpiCardChart(
            label="Tài sản ngắn hạn", 
            suffix="", format="{:.0f}"
            ).render(latest_current_assets)
    with col2:
        latest_current_liabilities = df_short_term_solvency_ratios.row(0, named=True)["current_liabilities"]
        KpiCardChart(
            label="Nợ ngắn hạn", 
            suffix="", format="{:.0f}"
            ).render(latest_current_liabilities)

    ## Khả năng chi trả lãi vay
    col1, col2, col3 = st.columns(3)
    with col1:
        latest_current_ratio = df_short_term_solvency_ratios.row(0, named=True)["current_ratio"]
        KpiCardChart(
            label="Chỉ số thanh toán ngắn hạn", 
            suffix="", format="{:.2f}"
            ).render(latest_current_ratio)
    with col2:
        latest_quick_ratio = df_short_term_solvency_ratios.row(0, named=True)["quick_ratio"]
        KpiCardChart(
            label="Chỉ số thanh toán nhanh", 
            suffix="", format="{:.2f}"
            ).render(latest_quick_ratio)
    with col3:
        latest_cash_ratio = df_short_term_solvency_ratios.row(0, named=True)["cash_ratio"]
        KpiCardChart(
            label="Chỉ số thanh toán tiền mặt", 
            suffix="", format="{:.2f}"
            ).render(latest_cash_ratio)

    ## Chu kì hoạt động kinh doanh
    col1, col2, col3 = st.columns(3)
    with col1:
        latest_days_inventory_outstanding = df_days_inventory_outstanding.row(0, named=True)["days_inventory_outstanding"]
        KpiCardChart(
            label="Vòng quay hàng tồn kho", 
            suffix=" Ngày", format="{:.0f}"
            ).render(latest_days_inventory_outstanding)
    with col2:
        latest_days_sales_outstanding = df_days_sales_outstanding.row(0, named=True)["days_sales_outstanding"]
        KpiCardChart(
            label="Vòng quay khoản phải thu ", 
            suffix=" Ngày", format="{:.0f}"
            ).render(latest_days_sales_outstanding)
    with col3:
        latest_operation_cycle = df_operating_cycle.row(0, named=True)["operation_cycle"]
        KpiCardChart(
            label="Chu kỳ hoạt động", 
            suffix=" Ngày", format="{:.0f}"
            ).render(latest_operation_cycle)

    st.divider()
    main_kpt = MarkDown(
        font_size="24px",    
        text="KHẢ NĂNG CHI TRẢ NỢ NGẮN HẠN"
    ).render()

    # Phân tích khả năng hoạt động liên tục
    line_chart = LineChartComponent(
                title="Chỉ số thanh toán ngắn hạn",
                x_col="period",
                y_cols=["current_ratio"],
                y_min=1.8,
                y_max=2.3,
            )
    line_chart.render(df_short_term_solvency_ratios)

    line_chart = LineChartComponent(
                title="Chỉ số thanh toán nhanh",
                x_col="period",
                y_cols=["quick_ratio"],
                y_min=1.5,
                y_max=2.0,
            )
    line_chart.render(df_short_term_solvency_ratios)

    line_chart = LineChartComponent(
                title="Chỉ số thanh toán tiền mặt",
                x_col="period",
                y_cols=["cash_ratio"],
                y_min=1.2,
                y_max=1.6,
            )
    line_chart.render(df_short_term_solvency_ratios)

    st.divider()
    main_kpt = MarkDown(
        font_size="24px",    
        text="CÁC CHỈ SỐ CHU KÌ HOẠT ĐỘNG LIÊN TỤC"
    ).render()

    st.write(
        """
            Chu kì hoạt động của doanh nghiệp chia thành hai giai đoạn. 
            + Giai đoạn 1: Hàng nằm trong kho. \n
                Nhập về kho -> Chế biến/bán -> Bán xong tạo ra doanh thu 
            + Giai đoạn 2: Nằm trên sổ xách \n
                Bán xong cho nợ -> Chờ khách trả tiền

            Chu kỳ hoạt động = Chỉ số quay vòng hàng tồn kho tính theo ngày + Chỉ số vòng quay khoản phải thu tính theo ngày
        """
    )

    line_chart = LineChartComponent(
                title="Chỉ số quay vòng hàng tồn kho tính theo ngày",
                x_col="period",
                y_cols=["days_inventory_outstanding"],
                y_min=56,
                y_max=75,
            )
    line_chart.render(df_days_inventory_outstanding)

    line_chart = LineChartComponent(
                title="Chỉ số vòng quay khoản phải thu tính theo ngày",
                x_col="period",
                y_cols=["days_sales_outstanding"],
                y_min=25,
                y_max=35,
            )
    line_chart.render(df_days_sales_outstanding)

    line_chart = LineChartComponent(
                title="Chu kỳ hoạt động",
                x_col="period",
                y_cols=["operation_cycle"],
                y_min=80,
                y_max=111,
            )
    line_chart.render(df_operating_cycle)

if __name__ in {"__main__", "__page__"}:
    liquidity_ratio()
