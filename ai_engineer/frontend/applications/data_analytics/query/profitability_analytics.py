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

roe_query = """
WITH data_ AS (
    SELECT 
        ist.year,
        ist.quarter,
        ist.stock_id,
        bs.total_assets,
        bs.total_equity,
        ist.net_revenue,
        ist.net_profit_after_corporate_income_tax,
        -- Xử lý bỏ chữ 'Q' trong quarter trước khi nhân/cộng
        (ist.year::integer * 4 + REPLACE(UPPER(ist.quarter), 'Q', '')::integer) AS time_order
    FROM public.fs_balance_sheet_type_one AS bs
    JOIN public.fs_income_statement_type_one AS ist
        ON bs.year = ist.year
        AND bs.stock_id = ist.stock_id
        AND bs.quarter = ist.quarter
    WHERE bs.stock_id = 'VNM'
),
ttm_data_ AS (
    SELECT 
        year,
        quarter,
        stock_id,
        SUM(net_revenue) OVER w AS ttm_net_revenue,
        SUM(net_profit_after_corporate_income_tax) OVER w AS ttm_net_profit,
        AVG(total_assets) OVER w AS avg_total_assets_ttm,
        AVG(total_equity) OVER w AS avg_total_equity_ttm,
        COUNT(*) OVER w AS ttm_count
    FROM data_
    WINDOW w AS (
        PARTITION BY stock_id 
        ORDER BY time_order 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    )
),
calculate_data_ AS (
    SELECT 
        year,
        quarter,
        stock_id,
        (ttm_net_profit::numeric / NULLIF(ttm_net_revenue::numeric, 0)) AS net_profit_margin_ttm,
        (ttm_net_revenue::numeric / NULLIF(avg_total_assets_ttm::numeric, 0)) AS asset_turnover_ttm,
        (avg_total_assets_ttm::numeric / NULLIF(avg_total_equity_ttm::numeric, 0)) AS financial_leverage_ttm
    FROM ttm_data_
    WHERE ttm_count = 4
)
SELECT 
    year,
    quarter,
    stock_id,
    ROUND(net_profit_margin_ttm, 4) AS net_profit_margin,
    ROUND(asset_turnover_ttm, 4) AS asset_turnover,
    ROUND(financial_leverage_ttm, 4) AS financial_leverage,
    ROUND((net_profit_margin_ttm * asset_turnover_ttm * financial_leverage_ttm) * 100, 2) AS roe
FROM calculate_data_
ORDER BY year DESC, quarter DESC
LIMIT 4
"""