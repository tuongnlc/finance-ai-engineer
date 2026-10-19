# Cong thuc: 
# Debt to Asset Ratio: Liabilities / Assets
# Debt to Equity Ratio: Liabilities / Equity
capital_structure = """
SELECT 
	year,
	quarter,
	stock_id,
	total_liabilities,
	total_assets,
	total_equity,
	ROUND(total_liabilities::numeric / total_assets::numeric,2) AS debt_to_asset,
	ROUND(total_liabilities::numeric / total_equity::numeric,2) AS debt_to_equity
FROM public.fs_balance_sheet_type_one
WHERE stock_id = 'VNM'
ORDER BY year DESC, quarter DESC
LIMIT 4
"""

# Interest Cover Ratio: EBIT / Interest Expense
# Lợi nhuận trước lãi vay và thuế (EBIT) = Lợi nhuận sau thuế + Chi phí thuế TNDN + Chi phí lãi vay
interest_cover = """
SELECT 
        year,
        quarter,
        gross_profit,
        selling_expenses,
        general_and_administrative_expenses,
        net_revenue,
		interest_expense,
        net_profit_after_corporate_income_tax + corporate_income_tax_expense + interest_expense AS ebit,
		ROUND((net_profit_after_corporate_income_tax + corporate_income_tax_expense + interest_expense)::numeric / interest_expense::numeric , 2) AS icr
FROM public.fs_income_statement_type_one
WHERE stock_id = 'VNM'
ORDER BY year DESC, quarter DESC
LIMIT 4
"""

# Operating Cash Flow-to-Total Debt Ratio: Operating Cash Flow / TOTAL Liabilities
operating_cash_flow_to_total_debt = """
WITH ordered_fs AS (
    -- Bước 1: Lấy dữ liệu và sắp xếp theo thứ tự thời gian tăng dần để chạy cửa sổ trượt
    SELECT 
        cf.year,
        cf.quarter,
        cf.stock_id,
        cf.net_cash_flows_from_operating_activities,
        bs.total_liabilities
    FROM public.fs_cash_flow_statement_type_one AS cf
    LEFT JOIN public.fs_balance_sheet_type_one AS bs
      ON cf.stock_id = bs.stock_id
     AND cf.quarter = bs.quarter
     AND cf.year = bs.year
    WHERE cf.stock_id = 'VNM'
),
ttm_calc AS (
    -- Bước 2: Tính tổng OCF của 4 quý gần nhất (TTM) bằng Window Function
    SELECT 
        year,
        quarter,
        stock_id,
        total_liabilities,
        SUM(net_cash_flows_from_operating_activities) OVER (
            PARTITION BY stock_id 
            ORDER BY year ASC, quarter ASC 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS ttm_ocf,
        -- Đếm số quý trong cửa sổ để đảm bảo đủ 4 quý liên tiếp
        COUNT(*) OVER (
            PARTITION BY stock_id 
            ORDER BY year ASC, quarter ASC 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS quarter_count
    FROM ordered_fs
)
-- Bước 3: Lọc lấy các kỳ đủ 4 quý TTM và sắp xếp giảm dần theo ý bạn
SELECT 
    year,
    quarter,
    stock_id,
    ttm_ocf AS net_cash_flows_from_operating_activities_ttm,
    total_liabilities,
    ROUND(ttm_ocf::numeric / NULLIF(total_liabilities::numeric, 0), 2) AS ocf_to_total_debt_ttm
FROM ttm_calc
WHERE quarter_count = 4  -- Chỉ lấy các dòng có đủ 4 quý (loại bỏ các kỳ lịch sử bị thiếu dữ liệu đầu bảng)
ORDER BY year DESC, quarter DESC
LIMIT 4
"""
