import json
import polars as pl
import matplotlib
matplotlib.use("Agg")



def load_and_prepare_data(url, columns):
    with open(url, "r") as file:
        data = json.load(file)

    financial_data = data["financial_data"]

    rows = [
        {'chi_tieu': key, 'ngay': date, 'gia_tri': val}
        for key, dates in financial_data.items()
        for date, val in dates.items()
    ]

    df = pl.DataFrame(rows)

    df_cleaned = df.with_columns(
        pl.col('gia_tri')
        .str.replace_all(r'\.', '')
        .str.replace_all(r'\(', '-')
        .str.replace_all(r'\)', '')
        .cast(pl.Int64)
    )

    df_pivoted = df_cleaned.pivot(
        on="chi_tieu",
        index="ngay",
        values="gia_tri",
    )

    df_ = df_pivoted.select(columns)
    return df_

bctc_url = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.json"
columns = ["ngay", "tai_san_ngan_han", "tai_san_dai_han"]

df = load_and_prepare_data(bctc_url, columns)
print(df)