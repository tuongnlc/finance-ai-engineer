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