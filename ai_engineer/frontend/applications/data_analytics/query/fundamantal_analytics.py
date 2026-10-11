
VNM_REVENUE_OVERVIEW = """
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

VNM_ASSETS_OVERVIEW = """
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

VNM_CASH_FLOW_OVERVIEW = """
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