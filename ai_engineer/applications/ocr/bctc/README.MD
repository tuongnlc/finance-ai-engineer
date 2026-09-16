# PIPELINE FOR OCR

## Tổng quan

Pipeline OCR chuyên dụng cho Báo cáo tài chính (BCTC) được thiết kế theo luồng xử lý tuần tự 4 bước, từ file PDF đầu vào đến các file text đã được chuẩn hóa bằng LLM. Sử dụng kết hợp PyMuPDF (xử lý PDF), OpenCV (tiền xử lý ảnh), Tesseract (OCR gốc), và LLM (chỉnh sửa chính tả + phân loại nội dung).

---

## 4 Bước xử lý chính

### STEP 1: READ PDF FILE AND SPLIT INTO PAGES
- **File thực thi**: [pdf_spliter.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/application/pdf_spliter.py)
- **Class**: `PDFSplititer`
- **Mô tả**: Đọc file PDF gốc, tách thành các trang thành nhiều file PDF đơn trang độc lập (`page_1.pdf`, `page_2.pdf`, ...)
- **Thư viện**: `pymupdf`
- **Input**: Đường dẫn file PDF gốc
- **Output**: Thư mục `preprocessing_resources/split_pdf/` chứa các file PDF đơn trang

---

### STEP 2: CONVERT PDF TO IMG
- **File thực thi**: [pdf_to_img.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/application/pdf_to_img.py)
- **Class**: `PDFToImg`
- **Mô tả**: Chuyển đổi từng file PDF đơn trang sang ảnh PNG chất lượng cao (DPI 300) để làm đầu vào cho bước OCR. Nếu `get_pixmap` không hỗ trợ param `dpi` sẽ fallback dùng `Matrix` zoom=4x.
- **Thư viện**: `pymupdf`
- **Input**: Thư mục chứa PDF đơn trang từ STEP 1
- **Output**: Thư mục `preprocessing_resources/pdf_to_img/` chứa các file ảnh `page__1.png`, `page__2.png`, ...

---

### STEP 3: PREPROCESS IMG + STEP 4: CALL LLM
Hiện tại 2 bước được gộp chung trong cùng 1 file: [img_preprocessing_and_call_llm.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/application/img_preprocessing_and_call_llm.py)
- **Lý do**: Do giới hạn quota LLM, ảnh cần xử lý tuần tự từng cái rồi gửi lên LLM để tránh bị rate limit. Trong tương lai có thể tách thành 2 file riêng và chạy song song.
- **Class**: `ImgOCRBCTCPreprocessing`

#### Bước 3.1: Tiền xử lý ảnh (Preprocessing)
Luồng xử lý ảnh trong `_preprocess_img()`:
1. **Đọc ảnh** `_read_img()`: Đọc ảnh PNG, chuyển từ RGB sang BGR (định dạng chuẩn OpenCV)
2. **Xoay ảnh** `rotate_img()`: Dùng Tesseract OSD (Orientation and Script Detection) phát hiện hướng ảnh, tự động xoay (0/90/180/270 độ)
3. **Phóng to ảnh** `_resize_img()`: Scale ảnh lên 3x bằng thuật toán INTER_CUBIC (nội suy 4x4 pixel lân cận) để tăng độ chính xác OCR
4. **Loại bỏ vùng màu** `_remove_color_block()`: Xóa con dấu (màu đỏ), chữ ký (màu xanh nước) bằng HSV mask + inpaint, sau đó chuyển sang ảnh grayscale
5. **Làm mịn ảnh** `_blur_img()`: Áp dụng bilateralFilter (sigma 9,75,75) làm mờ nhưng giữ nét chữ
6. **Lưu ảnh đã xử lý** vào `preprocessing_resources/img_preprocessing/`

#### Bước 3.2: OCR gốc bằng Tesseract
- `_img_to_text()`: Dùng pytesseract với config `--oem 1 --psm 4 --dpi 300 -c preserve_interword_spaces=10 -c tessedit_char_blacklist=▪•*■`, ngôn ngữ `vie+eng`
- `_mapping_wrong_words()`: Mapping các từ sai chính tả phổ biến trước khi gửi lên LLM (dùng dict `mapping_wrong_words`)

#### Bước 4: Gọi LLM (Gemini) làm sạch + phân loại
- `_call_llm()`: Sử dụng LangChain `ChatPromptTemplate` + `PydanticOutputParser` với schema `OutputOCR`
- Schema output của LLM (Pydantic Model `OutputOCR`):
  ```json
  {
    "type_of_document": "table | text",
    "type_of_content": "thông tin của doanh nghiệp | chỉ số tài chính | thuyết minh diễn giải",
    "wrong_word": {"từ_sai": "từ_đúng", ...},
    "new_text": "Nội dung đã được sửa lỗi chính tả, thêm dấu, giữ nguyên số liệu tài chính"
  }
- Prompt yêu cầu LLM:
  - Bước 1: Phân loại dạng văn bản (thường / bảng)
  - Bước 2: Phân loại nội dung (thông tin DN / chỉ số TC / thuyết minh)
  - Bước 3-4: Sửa lỗi chính tả, xuất danh sách mapping
  - Bước 5: Xuất text đã sạch, giữ nguyên cấu trúc bảng và số liệu tài chính

- `_save_as_txt_file()`: Lưu `new_text` vào thư mục output dưới dạng file `.txt`

---

# Input and output
+ **Input**: file PDF BCTC (đầu vào)
+ **Output**: Thư mục chứa nhiều file text:
  - `output_resources/ocr_result__page__N.txt` — Text cuối cùng của từng trang sau khi LLM xử lý
  - `preprocessing_resources/split_pdf/page_N.pdf` — PDF từng trang (bước 1)
  - `preprocessing_resources/pdf_to_img/page__N.png` — ảnh gốc (bước 2)
  - `preprocessing_resources/img_preprocessing/page__N.png` — ảnh đã tiền xử lý (bước 3)

---

## Cấu trúc thư mục

```
bctc/
├── application/                    # Module xử lý từng bước
│   ├── pdf_spliter.py                   # STEP 1: Split PDF
│   ├── pdf_to_img.py                      # STEP 2: PDF → Image
│   └── img_preprocessing_and_call_llm.py # STEP 3 & 4: Preprocess + OCR + LLM
├── use_case/
│   └── ocr_bctc.py          # Orchestrator: khởi tạo các class và chạy pipeline tuần tự
├── input_resources/            # Đặt file PDF BCTC cần OCR vào đây
├── preprocessing_resources/   # Output trung gian của từng bước
│   ├── split_pdf/            # Output STEP 1
│   ├── pdf_to_img/           # Output STEP 2
│   └── img_preprocessing/    # Output STEP 3
└── output_resources/          # Output cuối cùng (file .txt từng trang)
└── README.MD
```

---

## Orchestrator (Entry Point)

**File**: [ocr_bctc.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/use_case/ocr_bctc.py)

- **Class**: `OCRBCTCUseCase`
- **Luồng chạy** (`run()`):
  1. Khởi tạo 3 đối tượng xử lý (PDFSplititer, PDFToImg, ImgOCRBCTCPreprocessing) với config đường dẫn cứng
  2. Chạy STEP 1: `split_pdf()` → in ra số trang + tên file
  3. Chạy STEP 2: `convert_pdf_to_img(len_document)`
  4. Chạy STEP 3 + 4: `preprocess_img(len_document)` (loop từng trang tuần tự)
- **LLM Config**:
  - Model: `gemini-3.1-flash-lite`
  - Temperature: 0 (deterministic)
  - API Key: Lấy ngẫu nhiên 1 trong 8 key (`GCP_PROJECT_1` → `GCP_PROJECT_8`) từ `.env` để chia tải
- **Mapping sai chính tả mặc định**: dict `mapping_wrong_words` chứa ~30 cặp từ sai → đúng (Cổ phần, Nguồn vốn, Nợ phải trả, v.v.)

---

## Dependencies chính

| Thư viện | Chức năng
--- | ---
`pymupdf` | Split PDF, render PDF ra ảnh
`opencv-python` | Tiền xử lý ảnh (xoay, resize, inpaint, filter)
`pytesseract` | Phát hiện hướng ảnh (OSD) + OCR text gốc
`langchain-core` | Prompt template, Pydantic output parser, chain LLM
`langchain-google-genai` | Bridge gọi Gemini API
`pydantic` | Validate schema output của LLM
`Pillow` | Read image, convert định dạng ảnh
`numpy` | Xử lý ma trận ảnh
