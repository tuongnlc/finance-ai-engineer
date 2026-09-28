url = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.json"

# Step 1: Read json file
import json

with open(url, "r") as file:
    data = json.load(file)

financial_data = data["financial_data"]

print(financial_data)

# keyword_mapping


rows = [
    {'chi_tieu': key, 'ngay': date, 'gia_tri': val}
    for key, dates in financial_data.items()
    for date, val in dates.items()
]

import polars as pl

df = pl.DataFrame(rows)
print(df)

# # 3. Optional: Clean strings into numeric integers (handles dots and negative values in parentheses)
df_cleaned = df.with_columns(
    pl.col('gia_tri')
    .str.replace_all(r'\.', '')
    .str.replace_all(r'\(', '-')
    .str.replace_all(r'\)', '')
    .cast(pl.Int64)
)

# # 4. Pivot: chuyen cot chi_tieu thanh cac cot doc lap
df_pivoted = df_cleaned.pivot(
    on="chi_tieu",
    index="ngay",
    values="gia_tri",
)


df_ = df_pivoted.select(["ngay", "tai_san_ngan_han", "tai_san_dai_han"])



print(df_)

# csv_filename = "financial_data.csv"
# df_pivoted.write_csv(csv_filename)
# print(f"Đã xuất file thành công: {csv_filename}")

import matplotlib.pyplot as plt
import polars as pl

# Giả sử Polars DataFrame của bạn tên là df_pl
# (Nếu dữ liệu đang nằm trong biến df_pl)

# Chuyển đổi dữ liệu từ Polars sang dict hoặc pandas để matplotlib dễ xử lý
# Cách 1: Dùng .to_dicts() hoặc lấy trực tiếp cột
ngay_list = df_['ngay'].to_list()
ngan_han_list = df_['tai_san_ngan_han'].to_list()
dai_han_list = df_['tai_san_dai_han'].to_list()

# Thiết lập khung vẽ gồm 2 biểu đồ tròn (1 hàng, 2 cột)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for i in range(len(ngay_list)):
  labels = ['Tài sản ngắn hạn', 'Tài sản dài hạn']
  sizes = [ngan_han_list[i], dai_han_list[i]]
  colors = ['#ff9999', '#66b3ff']

  # Vẽ pie chart
  axes[i].pie(
      sizes,
      labels=labels,
      autopct='%1.1f%%',
      startangle=90,
      colors=colors,
      wedgeprops={'edgecolor': 'white'},
  )
  axes[i].set_title(
      f'Cơ cấu tài sản ngày {ngay_list[i]}', fontsize=14, fontweight='bold'
  )

plt.tight_layout()
plt.show()