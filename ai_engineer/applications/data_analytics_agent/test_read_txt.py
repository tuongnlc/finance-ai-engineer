# txt_url = '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/ocr_result__page__1.txt'
txt_urls_thong_tin_chung = [
   '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm/page_1__thong_tin_chung__thong_tin_chung.txt',
   '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm/page_2__thong_tin_chung__thong_tin_chung.txt',
   '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm/page_3__thong_tin_chung__thong_tin_chung.txt',
   '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm/page_4__thuyet_minh_bao_cao_tai_chinh_mau_b09__thong_tin_doanh_nghiep.txt',
   '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm/page_5__thuyet_minh_bao_cao_tai_chinh_mau_b09__nhung_thong_tin_khac.txt',
   '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm/page_6__thuyet_minh_bao_cao_tai_chinh_mau_b09__nhung_thong_tin_khac.txt'
]

txt_urls_bctc = [
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_7__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_8__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_9__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_10__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_11__bao_cao_ket_qua_hoat_dong_kinh_doanh_mau_b02.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_12__bao_cao_ket_qua_hoat_dong_kinh_doanh_mau_b02.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_13__bao_cao_luu_chuyen_tien_te_mau_b03.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_14__bao_cao_luu_chuyen_tien_te_mau_b03.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_15__bao_cao_luu_chuyen_tien_te_mau_b03.txt'
]

txt_urls_bcdkt = [
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_7__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_8__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_9__bang_can_doi_ke_toan_mau_b01.txt',
    '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/page_10__bang_can_doi_ke_toan_mau_b01.txt',
]

output_list = []

for txt_url in txt_urls_thong_tin_chung:
    with open(txt_url, "r") as file:
        content = file.read()
        output_list.append(
            # content
            {
                "txt_url": txt_url.split('/')[-1],
                "content": content
            }
        )

print(output_list)
# + "Nếu type_of_report từ bước 1 là Bảng cân đối kế toán (Mẫu B 01). Trích xuất những thông tin sau:\n"
#     + "- Tài sản ngắn hạn\n"
#     + "- Tiền và các khoản tương đương tiền\n"
#     + "- Tiền\n"
#     + "- Các khoản tương đương tiền\n"
#     + "Nếu type_of_report từ bước 2 là Báo cáo kết quả hoạt động kinh doanh (Mẫu B 02). Trích xuất những thông tin sau:\n"
#     + "Doanh thu bán hàng và cung cấp dịch vụ\n"
#     + "Các khoản giảm trừ doanh thu\n"
#     + "Doanh thu thuần về bán hàng và cung cấp dịch vụ\n"
#     + "Nếu type_of_report từ bước 2 là Báo cáo lưu chuyển tiền tệ (Mẫu B 03). Trích xuất những thông tin sau:\n"
#     + "Lợi nhuận kế toán trước thuế\n"
#     + "Khấu hao\n"