from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
from ai_engineer.shared.llm.create_llm import create_gemini_llm
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel

class OutputContent(BaseModel):
    financial_data: dict
    

parser = PydanticOutputParser(pydantic_object=OutputContent)

prompt = ChatPromptTemplate.from_template(
    (
    "PERSONA Bạn là một chuyên gia tài chính, hiểu rõ các thuật ngữ tài chính, kinh tế.\n\n"
    + "[TASK]Nhiệm vụ của bạn là đọc đoạn văn nhỏ được tách ra từ báo cáo tài chính. Và tiến hành những điều sau.\n"
    + "Bước 1: Đọc nội dung từng dòng và trích xuất tất cả thông tin tài chính liên quan. Đảm bảo không bỏ sót bất cứ thông tin nào\n"
        + " [FORMAT] Đầu ra bắt buộc phải là một đối tượng JSON hợp lệ, không kèm theo bất kỳ văn bản giải thích hay Markdown nào ngoài khối JSON. Theo sát EXAMPLE OUTPUT phía dưới {format_instructions}\n"
        + " Giá trị key của output chuyển thành tiếng việt không dấu, ngan cach nhau bang dau _. Ví dụ: \"Tài sản ngắn hạn\" -> \"tai_san_ngan_han\"\n"
    + "--- START OF EXAMPLE ---\n"
    + "[EXAMPLE INPUT]\n"
    + "\n"
    + "\n"
    + "[EXAMPLE OUTPUT]\n"
    + "{{\n"
    + "    \"financial_data\": {{\n"
    + "        \"Tài sản ngắn hạn\": {{\n"
    + "            \"30/6/2026\": \"40.892.259.162.483\",\n"
    + "            \"1/1/2026\": \"36.249.794.729.810\"\n"
    + "        }},\n"
    + "        \"Tiền và các khoản tương đương tiền\": \"38,746.85\",\n"
    + "        \"Tiền\": \"38,746.85\",\n"
    + "        \"Các khoản tương đương tiền\": \"38,746.85\"\n"
    + "    }}\n"
    + "}}\n"
    + "--- END OF EXAMPLE ---\n"
    + "\n"
    + "{text}"
    )
).partial(format_instructions=parser.get_format_instructions())

llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)
structured_llm = llm.with_structured_output(OutputContent)

chain_ = prompt | structured_llm 

text_ = """
Công ty Cổ phần Sữa Việt Nam và các công ty con Báo cáo tình hình tài chính hợp nhất tại ngày 30 tháng 6 năm 2026 Mẫu B 01a - DN/HN (Ban hành theo Thông tư số 43/2026/TT-BTC ngày 20 tháng 4 năm 2026 của Bộ Tài chính) Mã số Thuyết minh 30/6/2026 VND 1/1/2026 VND (Đã phân loại lại) TÀI SẢN Tài sản ngắn hạn (100 = 110 + 120 + 130 + 140 + 150+ 160) 100 40.892.259.162.483 36.249.794.729.810 Tiền và các khoản tương đương tiền 110 V.1 4.535.672.366.831 1.794.879.718.871 Tiền 111 3.763.870.966.831 1.630.879.718.871 Các khoản tương đương tiền 112 771.801.400.000 164.000.000.000 Các khoản đầu tư tài chính ngắn hạn 120 21.967.555.447.949 21.891.390.273.656 Chứng khoán kinh doanh 121 V.4(a) 1.284.231.445 1.288.677.349 Dự phòng giảm giá chứng khoán kinh doanh 122 V.4(a) (817.155.511) (849.021.293) Đầu tư nắm giữ đến ngày đáo hạn 123 V.4(b) 21.967.088.372.015 21.890.950.617.600 Các khoản phải thu ngắn hạn 130 5.949.416.079.195 5.489.574.577.332 Phải thu khách hàng 131 5.150.211.936.876 4.701.653.413.423 Trả trước cho người bán 132 513.178.822.738 443.955.080.617 Phải thu ngắn hạn khác 135 V.3(a) 305.700.755.983 377.743.023.611 Dự phòng phải thu khó đòi 136 V.2 (19.675.436.402) (33.776.940.319) Hàng tồn kho 140 V.5 7.720.280.777.044 6.529.979.921.580 Hàng tồn kho 141 7.768.442.112.731 6.588.578.280.201 Dự phòng giảm giá hàng tồn kho 142 (48.161.335.687) (55.598.358.621) Tài sản sinh học ngắn hạn 150 354.177.533.828 299.531.573.678 Súc vật nuôi lấy sản phẩm một lần 151 V.8(a) 331.747.047.285 297.901.392.714 Cây trồng theo mùa vụ hoặc lấy sản phẩm một lần ngắn hạn 152 22.430.486.543 1.630.180.964 Tài sản ngắn hạn khác 160 365.156.957.636 244.438.664.693 Chi phí chờ phân bổ ngắn hạn 161 V.11(a) 196.299.598.634 150.006.422.830 Thuế giá trị gia tăng được khấu trừ 162 144.125.539.652 64.351.825.929 Thuế phải thu Nhà nước 163 24.731.819.350 30.080.415.934 Các thuyết minh đính kèm là bộ phận hợp thành của báo cáo tài chính hợp nhất giữa niên độ này"""

# response = chain_.invoke({"text": text_})
# response_dict = response.model_dump()
# print(response_dict)

# # Build dataframe
response_dict = {'financial_data': {'tai_san_ngan_han': {'30/6/2026': '40.892.259.162.483', '1/1/2026': '36.249.794.729.810'}, 'tien_va_cac_khoan_tuong_duong_tien': {'30/6/2026': '4.535.672.366.831', '1/1/2026': '1.794.879.718.871'}, 'tien': {'30/6/2026': '3.763.870.966.831', '1/1/2026': '1.630.879.718.871'}, 'cac_khoan_tuong_duong_tien': {'30/6/2026': '771.801.400.000', '1/1/2026': '164.000.000.000'}, 'cac_khoan_dau_tu_tai_chinh_ngan_han': {'30/6/2026': '21.967.555.447.949', '1/1/2026': '21.891.390.273.656'}, 'chung_khoan_kinh_doanh': {'30/6/2026': '1.284.231.445', '1/1/2026': '1.288.677.349'}, 'du_phong_giam_gia_chung_khoan_kinh_doanh': {'30/6/2026': '(817.155.511)', '1/1/2026': '(849.021.293)'}, 'dau_tu_nam_giu_den_ngay_dao_han': {'30/6/2026': '21.967.088.372.015', '1/1/2026': '21.890.950.617.600'}, 'cac_khoan_phai_thu_ngan_han': {'30/6/2026': '5.949.416.079.195', '1/1/2026': '5.489.574.577.332'}, 'phai_thu_khach_hang': {'30/6/2026': '5.150.211.936.876', '1/1/2026': '4.701.653.413.423'}, 'tra_truoc_cho_nguoi_ban': {'30/6/2026': '513.178.822.738', '1/1/2026': '443.955.080.617'}, 'phai_thu_ngan_han_khac': {'30/6/2026': '305.700.755.983', '1/1/2026': '377.743.023.611'}, 'du_phong_phai_thu_kho_doi': {'30/6/2026': '(19.675.436.402)', '1/1/2026': '(33.776.940.319)'}, 'hang_ton_kho': {'30/6/2026': '7.720.280.777.044', '1/1/2026': '6.529.979.921.580'}, 'hang_ton_kho_gia_tri': {'30/6/2026': '7.768.442.112.731', '1/1/2026': '6.588.578.280.201'}, 'du_phong_giam_gia_hang_ton_kho': {'30/6/2026': '(48.161.335.687)', '1/1/2026': '(55.598.358.621)'}, 'tai_san_sinh_hoc_ngan_han': {'30/6/2026': '354.177.533.828', '1/1/2026': '299.531.573.678'}, 'suc_vat_nuoi_lay_san_pham_mot_lan': {'30/6/2026': '331.747.047.285', '1/1/2026': '297.901.392.714'}, 'cay_trong_theo_mua_vu_hoac_lay_san_pham_mot_lan_ngan_han': {'30/6/2026': '22.430.486.543', '1/1/2026': '1.630.180.964'}, 'tai_san_ngan_han_khac': {'30/6/2026': '365.156.957.636', '1/1/2026': '244.438.664.693'}, 'chi_phi_cho_phan_bo_ngan_han': {'30/6/2026': '196.299.598.634', '1/1/2026': '150.006.422.830'}, 'thue_gia_tri_gia_tang_duoc_khau_tru': {'30/6/2026': '144.125.539.652', '1/1/2026': '64.351.825.929'}, 'thue_phai_thu_nha_nuoc': {'30/6/2026': '24.731.819.350', '1/1/2026': '30.080.415.934'}}}# type_of_report = dict_['type_of_report']
# print(type_of_report)

financial_data = response_dict['financial_data']
print(financial_data)
print(" ")
print(" ")

rows = [
    {'chi_tieu': key, 'ngay': date, 'gia_tri': val}
    for key, dates in financial_data.items()
    for date, val in dates.items()
]

# 2. Create the initial Polars DataFrame
import polars as pl

df = pl.DataFrame(rows)

# 3. Optional: Clean strings into numeric integers (handles dots and negative values in parentheses)
df_cleaned = df.with_columns(
    pl.col('gia_tri')
    .str.replace_all(r'\.', '')
    .str.replace_all(r'\(', '-')
    .str.replace_all(r'\)', '')
    .cast(pl.Int64)
)

# 4. Pivot: chuyen cot chi_tieu thanh cac cot doc lap
df_pivoted = df_cleaned.pivot(
    on="chi_tieu",
    index="ngay",
    values="gia_tri",
)

print(df_pivoted)

# csv_filename = "financial_data.csv"
# df_cleaned.write_csv(csv_filename)
# print(f"Đã xuất file thành công: {csv_filename}")