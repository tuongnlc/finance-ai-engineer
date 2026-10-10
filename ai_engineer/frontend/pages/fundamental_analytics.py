import polars as pl
import streamlit as st
from ai_engineer.frontend.components.chart.table_chart import TableChart
from ai_engineer.frontend.components.chart.line_chart import LineChartComponent
from ai_engineer.frontend.components.chart.kpi_cart_chart import KpiCardChart
from ai_engineer.frontend.applications.data_analytics.integrations.db import load_data_from_postgres_polars


VNM_REVENUE_QUERY = """
        SELECT 
            year,
            quarter,
            net_revenue, 
            gross_profit,
            net_operating_profit,
            total_accounting_profit_before_tax,
            net_profit_after_corporate_income_tax,
            ROUND((net_profit_after_corporate_income_tax::numeric / net_revenue::numeric) * 100, 1) AS net_profit_margin
        FROM public.fs_income_statement_type_one
        WHERE stock_id = 'VNM'
        ORDER BY year DESC, quarter DESC
        LIMIT 4
    """

VNM_ASSETS_QUERY = """
        SELECT 
            year,
            quarter,
            current_assets,
            cash_and_cash_equivalents,
            short_term_financial_investments,
            short_term_receivables,
            inventories,
            ROUND((current_assets::numeric / current_liabilities::numeric),2) as current_ratio,
            ROUND((total_assets::numeric / total_liabilities::numeric),2) as equity_multiplier
        FROM public.fs_balance_sheet_type_one
        WHERE stock_id = 'VNM'
        ORDER BY year DESC, quarter DESC
        LIMIT 4
    """

VNM_CASH_FLOW = """
        SELECT
            year,
            quarter,
            net_cash_flows_from_operating_activities,
            net_cash_flows_from_financing_activities,
            net_cash_flows_from_investing_activities,
            net_change_in_cash,
            cash_and_cash_equivalents_at_end_of_period,
            (net_cash_flows_from_operating_activities - net_cash_flows_from_investing_activities)/1000 AS free_cash_flow
        FROM 
            public.fs_cash_flow_statement_type_one
        WHERE stock_id = 'VNM'  
        ORDER BY year DESC, quarter DESC
        LIMIT 4
    """

def fundamental_analytics():
    vnm_df = load_data_from_postgres_polars(VNM_REVENUE_QUERY)
    table_ts = load_data_from_postgres_polars(VNM_ASSETS_QUERY)
    table_cash_flow = load_data_from_postgres_polars(VNM_CASH_FLOW)
    
    st.set_page_config(
        page_title="Fundamental Analytics",
        layout="wide"  # Mặc định là "centered", đổi thành "wide" để tràn viền
    )

    # st.markdown(
    #     """
    #     <p style='font-size: 30px; font-weight: bold;color: #1583b4;'>PHÂN TÍCH CƠ BẢN</p>
    #     """,
    #     unsafe_allow_html=True,
    # )

    st.sidebar.markdown(
        """
        <p style='font-size: 20px; font-weight: bold;color: #c77f44;'>Chọn doanh nghiệp</p>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.selectbox("Lựa chọn doanh nghiệp để phân tích", 
        [
            "VNM", 
            "ACB"
        ]
    )

    st.sidebar.selectbox("Lựa chọn loại phân tích", 
        [
            "Khả năng sinh lợi", 
            "Chỉ số thanh khoản",
            "Khả năng quản trị nợ"
        ]
    )

    # st.divider()
    st.markdown(
        """
        <p style='font-size: 24px; font-weight: bold;color: #1583b4;'>CÁC CHỈ SỐ CƠ BẢN</p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    # latest = vnm_df.row(0, named=True)

    with col1:
        latest_current_ratio = table_ts.row(0, named=True)["current_ratio"]
        KpiCardChart(label="Chỉ số thanh toán ngắn hạn", suffix="", format="{:.2f}").render(latest_current_ratio)
    with col2:
        latest_net_profit_margin = vnm_df.row(0, named=True)["net_profit_margin"]
        KpiCardChart(label="Biên lợi nhuận thuần", suffix="%", format="{}").render(latest_net_profit_margin)
    with col3:
        latest_equity_multiplier = table_ts.row(0, named=True)["equity_multiplier"]
        KpiCardChart(label="Hệ số vốn", suffix="", format="{:,.0f}").render(
            latest_equity_multiplier
        )
    with col4:
        latest_free_cash_flow = table_cash_flow.row(0, named=True)["free_cash_flow"]
        KpiCardChart(label="Dòng tiền tự do", suffix=" tỷ", format="{:,.0f}").render(
            latest_free_cash_flow
        )


    st.divider()
    

    if not vnm_df.is_empty():
        vnm_df = vnm_df.with_columns(
            (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
        )

        # st.write("Phân tích khả năng sinh lợi")

        # st.write("Tổng quan doanh thu và lợi nhuận")
        st.markdown(
            "<p style='font-size: 24px; font-weight: bold;color: #1583b4;'>DOANH THU VÀ LỢI NHUẬN</p>",
            unsafe_allow_html=True,
        )
        
        table_vnm = TableChart()
        table_vnm.render(vnm_df.select(
            ["period", "net_revenue", "gross_profit", "net_operating_profit", "net_profit_after_corporate_income_tax"]))

        with st.container(border=True):
            # st.subheader("Tổng quan doanh thu và lợi nhuận")
            col1, col2 = st.columns(2)
            with col1:
                line_chart = LineChartComponent(
                    title="Doanh thu thuần về bán hàng và cung cấp dịch vụ",
                    x_col="period",
                    y_cols=["net_revenue"],
                    y_min=16000000,
                    y_max=19000000,
                )
                line_chart.render(vnm_df)
            with col2:
                line_chart = LineChartComponent(
                    title="Lợi nhuận gộp về bán hàng và cung cấp dịch vụ",
                    x_col="period",
                    y_cols=["gross_profit"],
                    y_min=6000000,
                    y_max=9000000,
                )
                line_chart.render(vnm_df)
            col3, col4 = st.columns(2)
            with col3:
                line_chart = LineChartComponent(
                    title="Lợi nhuận thuần từ hoạt động kinh doanh",
                    x_col="period",
                    y_cols=["net_operating_profit"],
                    y_min=2500000,
                    y_max=4000000,
                )
                line_chart.render(vnm_df)
            with col4:
                line_chart = LineChartComponent(
                    title="Lợi nhuận kế toán trước thuế",
                    x_col="period",
                    y_cols=["total_accounting_profit_before_tax"],
                    y_min=2500000,
                    y_max=4000000,
                )
                line_chart.render(vnm_df)

    st.divider()
    st.markdown(
            "<p style='font-size: 24px; font-weight: bold;color: #1583b4;'>TÀI SẢN NGẮN HẠN</p>",
            unsafe_allow_html=True,
        )
    
    table_ts = table_ts.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )
    # table_ts.render(table_ts)
    if not table_ts.is_empty():
        line_chart = LineChartComponent(
                title="Tổng quan tài sản ngắn hạn",
                x_col="period",
                y_cols=["current_assets"],
                y_min=35000000,
                y_max=42000000,
            )
        line_chart.render(table_ts)

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                line_chart = LineChartComponent(
                    title="Tiền và các khoản tương đương tiền",
                    x_col="period",
                    y_cols=["cash_and_cash_equivalents"],
                    y_min=1500000,
                    y_max=5200000,
                )
                line_chart.render(table_ts)
            with col2:
                line_chart = LineChartComponent(
                    title="Các khoản đầu tư tài chính ngắn hạn",
                    x_col="period",
                    y_cols=["short_term_financial_investments"],
                    y_min=20000000,
                    y_max=25000000,
                )
                line_chart.render(table_ts)
            col3, col4 = st.columns(2)
            with col3:
                line_chart = LineChartComponent(
                    title="Các khoản phải thu ngắn hạn",
                    x_col="period",
                    y_cols=["short_term_receivables"],
                    y_min=5500000,
                    y_max=6127719,
                )
                line_chart.render(table_ts)
            with col4:
                line_chart = LineChartComponent(
                    title="Hàng tồn kho",
                    x_col="period",
                    y_cols=["inventories"],
                    y_min=6308583,
                    y_max=7820281,
                )
                line_chart.render(table_ts)
    else: 
        st.info("Không có dữ liệu tài sản ngắn hạn VNM từ CSDL.")
    
    st.divider()
    st.markdown(
            "<p style='font-size: 24px; font-weight: bold;color: #1583b4;'>LƯU CHUYỂN TIỀN TỆ</p>",
            unsafe_allow_html=True,
    )

    
    table_cash_flow = table_cash_flow.with_columns(
        (pl.col("year").cast(pl.Utf8) + pl.lit("__") + pl.col("quarter").cast(pl.Utf8)).alias("period")
    )
    
    if not table_cash_flow.is_empty():
        line_chart = LineChartComponent(
                title="Tiền và tương đương tiền cuối kỳ",
                x_col="period",
                y_cols=["cash_and_cash_equivalents_at_end_of_period"],
                y_min=1794870,
                y_max=5254466,
            )
        line_chart.render(table_cash_flow)

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                line_chart = LineChartComponent(
                    title="Lưu chuyển tiền thuần từ hoạt động kinh doanh",
                    x_col="period",
                    y_cols=["net_cash_flows_from_operating_activities"],
                    y_min=269325,
                    y_max=3204451,
                )
                line_chart.render(table_cash_flow)
            with col2:
                line_chart = LineChartComponent(
                    title="Lưu chuyển tiền thuần từ hoạt động tài chính",
                    x_col="period",
                    y_cols=["net_cash_flows_from_financing_activities"],
                    y_min=-4822750,
                    y_max=905708,
                )
                line_chart.render(table_cash_flow)
            col3, col4 = st.columns(2)
            with col3:
                line_chart = LineChartComponent(
                    title="Lưu chuyển tiền thuần từ hoạt động đầu tư",
                    x_col="period",
                    y_cols=["net_cash_flows_from_investing_activities"],
                    y_min=-980996,
                    y_max=1273823,
                )
                line_chart.render(table_cash_flow)
            with col4:
                line_chart = LineChartComponent(
                    title="Lưu chuyển tiền thuần trong kỳ",
                    x_col="period",
                    y_cols=["net_change_in_cash"],
                    y_min=-3357638,
                    y_max=2755805,
                )
                line_chart.render(table_cash_flow)



if __name__ in {"__main__", "__page__"}:
    fundamental_analytics()
