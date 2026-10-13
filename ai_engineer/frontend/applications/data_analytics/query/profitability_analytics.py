profit_margin_cascade = """
    SELECT 
        year,
        quarter,
        net_revenue, 
        gross_profit,
        net_operating_profit
    FROM public.fs_income_statement_type_one
    WHERE stock_id = 'VNM'
    ORDER BY year DESC, quarter DESC
    LIMIT 4
"""

#Capital Efficiency
capital_efficiency = """
    SELECT 
        roa,
        roe,
        roic
    FROM public.fs_financial_statistics_overview_type_one
    WHERE stock_id = 'VNM'
    ORDER BY year DESC, quarter DESC
    LIMIT 4
"""

# Operating Margin
operating_margin_query = """
    SELECT 
        year,
        quarter,
        gross_profit,
        selling_expenses,
        general_and_administrative_expenses,
        net_revenue,
        ROUND(
        (
            (gross_profit - selling_expenses - general_and_administrative_expenses)::numeric / 
        net_revenue::numeric
        ), 2) AS operating_margin   
    FROM public.fs_income_statement_type_one
    WHERE stock_id = 'VNM'
    ORDER BY year DESC, quarter DESC
    LIMIT 4
"""

#Operating Asset Turnover
operating_asset_turnover_query = """
    WITH income_statement_data
    AS
    (
        SELECT 
            year,
            quarter,
            stock_id,
            net_revenue
        FROM public.fs_income_statement_type_one
    ),

    balance_sheet_data AS 
    (
        SELECT 
            year,
            quarter,
            stock_id,
            short_term_receivables,
            inventories,
            fixed_assets,
            long_term_assets_in_progress
        FROM public.fs_balance_sheet_type_one
    ),

    revenue_and_operating_data AS (
    SELECT 
        bc.year,
        bc.quarter,
        bc.stock_id,
        ist.net_revenue,
        ROUND(ist.net_revenue::numeric*0.02,0) + bc.short_term_receivables + bc.inventories + bc.fixed_assets + bc.long_term_assets_in_progress AS operating_assets
    FROM 
    balance_sheet_data AS bc
    LEFT JOIN income_statement_data AS ist
    ON bc.year=ist.year AND bc.quarter = ist.quarter AND bc.stock_id = ist.stock_id
    ),

    final_data_with_previous_assets AS(
        SELECT 
            year,
            quarter,
            stock_id,
            net_revenue,
            operating_assets,
            LAG(operating_assets) OVER (PARTITION BY stock_id ORDER BY year, quarter) AS prev_operating_assets
        FROM revenue_and_operating_data
    )

    SELECT 
        year,
        quarter,
        stock_id,
        net_revenue,
        operating_assets,
        
        -- 1. Tính Tài sản hoạt động bình quân (Average Operating Assets)
        -- Nếu là quý đầu tiên không có dữ liệu quý trước, tạm lấy bằng chính quý đó
        ROUND(COALESCE((operating_assets + prev_operating_assets) / 2.0, operating_assets),0) AS avg_operating_assets,
        
        -- 2. Tính tỷ suất vòng quay tài sản vận hành (OAT)
        -- Lưu ý: net_revenue là doanh thu quý. Nếu bạn muốn quy đổi ra năm (Annualized OAT), hãy nhân net_revenue với 4.
        ROUND(
            CAST(net_revenue AS NUMERIC) / NULLIF(COALESCE((operating_assets + prev_operating_assets) / 2.0, operating_assets), 0), 
            2
        ) AS oat_ratio
    FROM final_data_with_previous_assets
    WHERE stock_id = 'VNM'
    ORDER BY year DESC, quarter DESC
    LIMIT 4
"""

#Equity Multiplier - Hệ số vốn
equity_multiplier_query = """
    SELECT 
        year,
        quarter,
        stock_id,
        total_assets,
        total_equity,
        ROUND(total_assets::numeric / total_equity::numeric, 2) AS equity_multiplier 
    FROM public.fs_balance_sheet_type_one
    WHERE stock_id = 'VNM'
    ORDER BY year DESC, quarter DESC
    LIMIT 4
"""
