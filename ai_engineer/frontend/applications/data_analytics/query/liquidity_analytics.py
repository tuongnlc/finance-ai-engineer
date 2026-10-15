# Short-term Solvency Ratios)
short_term_solvency_ratios_query = """
    SELECT 
	year,
	quarter,
	stock_id,
	current_assets, -- Tài sản ngắn hạn
	current_liabilities, -- Nợ ngắn hạn
	cash_and_cash_equivalents, -- Tiền và tương đương tiền
	short_term_financial_investments, -- Đầu tư tài chính ngắn hạn
	short_term_receivables, -- phải thu khách hàng
	ROUND(current_assets::numeric / current_liabilities::numeric, 2) AS current_ratio,
	ROUND(
		(cash_and_cash_equivalents + short_term_financial_investments + short_term_receivables)::numeric / 
			current_liabilities::numeric, 2
	) AS quick_ratio,
	ROUND(
		(cash_and_cash_equivalents + short_term_financial_investments)::numeric / 
			current_liabilities::numeric, 2
	) AS cash_ratio
FROM public.fs_balance_sheet_type_one
WHERE stock_id = 'VNM'
ORDER BY year DESC, quarter DESC
LIMIT 4
"""

# Days Inventory Outstanding
days_inventory_outstanding_query = """
WITH inventory_with_lag AS (
    SELECT 
        year,
        quarter,
        stock_id,
        inventories AS ending_inventory,
        -- Lấy giá trị hàng tồn kho của quý trước liền kề
        LAG(inventories, 1) OVER (PARTITION BY stock_id ORDER BY year, quarter) AS beginning_inventory
    FROM public.fs_balance_sheet_type_one
    WHERE stock_id = 'VNM'
),

calculated_data AS (
SELECT 
    ist.year,
    ist.quarter,
    ist.stock_id,
    CASE 
        WHEN beginning_inventory IS NOT NULL THEN (beginning_inventory + ending_inventory) / 2.0
        ELSE beginning_inventory -- Quý đầu tiên có dữ liệu trong bảng sẽ chưa có quý trước để tính
    END AS average_inventories,
	ist.cost_of_goods_sold
FROM inventory_with_lag AS ass
LEFT JOIN 
(
	SELECT 
		year,
		quarter,
		stock_id,
		cost_of_goods_sold
	FROM public.fs_income_statement_type_one
	WHERE stock_id = 'VNM'
) AS ist
ON 
ass.stock_id = ist.stock_id
AND ass.year = ist.year
AND ass.quarter = ist.quarter
)

SELECT 
	year,
	quarter,
	stock_id,
	average_inventories,
	cost_of_goods_sold,
	ROUND(average_inventories/(cost_of_goods_sold/90), 0) AS days_inventory_outstanding
FROM calculated_data
ORDER BY year DESC, quarter DESC
LIMIT 4
"""

# Days Sales Outstanding
days_sales_outstanding_query = """
WITH inventory_with_lag AS (
    SELECT 
        year,
        quarter,
        stock_id,
        short_term_receivables AS end_short_term_receivables,
        -- Lấy giá trị hàng tồn kho của quý trước liền kề
        LAG(short_term_receivables, 1) OVER (PARTITION BY stock_id ORDER BY year, quarter) AS begin_short_term_receivables
    FROM public.fs_balance_sheet_type_one
    WHERE stock_id = 'VNM'
),
-- 
calculated_data AS (
SELECT 
    ist.year,
    ist.quarter,
    ist.stock_id,
    CASE 
        WHEN begin_short_term_receivables IS NOT NULL THEN (begin_short_term_receivables + end_short_term_receivables) / 2.0
        ELSE begin_short_term_receivables -- Quý đầu tiên có dữ liệu trong bảng sẽ chưa có quý trước để tính
    END AS average_short_term_receivables,
	ist.net_revenue
FROM inventory_with_lag AS ass
LEFT JOIN 
(
	SELECT 
		year,
		quarter,
		stock_id,
		net_revenue
	FROM public.fs_income_statement_type_one
	WHERE stock_id = 'VNM'
) AS ist
ON 
ass.stock_id = ist.stock_id
AND ass.year = ist.year
AND ass.quarter = ist.quarter
)

SELECT 
	year,
	quarter,
	stock_id,
	average_short_term_receivables,
	net_revenue,
	ROUND(average_short_term_receivables/(net_revenue/90), 0) AS days_sales_outstanding
FROM calculated_data
ORDER BY year DESC, quarter DESC
LIMIT 4
"""

