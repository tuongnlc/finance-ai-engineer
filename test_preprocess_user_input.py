import json
import re
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
load_dotenv()

from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

preprocess_user_input_template = [
    {
        "role": "system",
        "content": (
            "Role: Bạn là bộ tiền xử lý câu hỏi (Query Preprocessing Agent) cho hệ thống RAG tài chính. "
            "Nhiệm vụ của bạn là chuyển user query thành tiếng việt có dấu, "
            "sau đó phân tích input của người dùng để trích xuất các thực thể và định hướng truy xuất dữ liệu.\n"
            "\n"
            "---\n"
            "\n"
            "### Nhiệm vụ khi nhận input của user:\n"
            "1. **Phân loại câu hỏi của user (question_type). Luôn luôn trả về các kết quả như bên dưới**\n"
                '- Câu hỏi chung về tin tức tài chính, kinh tế, biến động thị trường, luật doanh nghiệp, chính sách của nhà nước liên quan tới kinh tế. Kết quẩ trả về là tin tức thị trường'
                '- Câu hỏi chung về tin tức trong quản trị doanh nghiệp, biến động doanh nghiệp, nhân sự doanh nghiệp. Kết quả trả về là tin tức doanh nghiệp'
                '- Câu hỏi cụ thể về tình hình tài chính doanh nghiệp kết quả trả về là con số cụ thể: doanh thu, lợi nhuận, chi phí, số tuyệt đối, ROE, ROA, NIM, NPL, P/E, EPS, tỷ suất, hệ số. Kết quả trả về tài chính doanh nghiệp'
                '- Câu hỏi không liên quan tới thị trường, kinh tế, tài chính. Kết quả trả về là câu hỏi không liên quan'
            "2. **Phân loại nội dung câu hỏi (main_topic). Luôn luôn trả về các kết quả như bên dưới **\n"
                '- Nội dung 1: kinh tế vĩ mô & chính sách. Bao gồm các nội dung: Phân tích Kinh tế vĩ mô, Chính sách tiền tệ & Ngân hàng Trung ương, Yếu tố địa chính trị & Năng lượng, Biến động thị trường toàn cầu. Trả về Kinh tế vĩ mô & Chính sách'
                '- Nội dung 2: thị trường & giao dịch. Bao gồm các nội dung: Biến động thị trường, Thị trường chứng khoán cơ sở, Thị trường chứng khoán phái sinh, Thị trường vàng, ngoại hối & Hàng hóa,'
                'Giao dịch & Tài chính, Giao dịch cổ phiếu & Nội bộ, Thị trường chứng khoán, Thị trường chứng khoán cơ sở '
                '(Giao dịch cổ phiếu, Giao dịch nội bộ...), Thị trường chứng khoán phái sinh. Trả về Thị trường & Giao dịch. Trả về Thị trường & Giao dịch'
                '- Nội dung 3: quản trị doanh nghiệp. Bao gồm các nội dung: Biến động doanh nghiệp, Thách thức & Rủi ro, Chiến lược & Thị trường, Doanh nghiệp & Dự án, Quản trị rủi ro doanh nghiệp, Quản trị nguồn nhân lực chiến lược. Trả về Quản trị Doanh nghiệp'
                '- Nội dung 4: tài chính doanh nghiệp. Bao gồm các nội dung: Tài chính & Quản trị doanh nghiệp, Dự báo tài chính & Tăng trưởng, Cơ cấu doanh thu & Các mảng kinh doanh, Huy động vốn & Trái phiếu, Định giá, Sự kiện IPO, Quản trị tài chính (Financial Management), Tài chính - Ngân hàng. Trả về Tài chính Doanh nghiệp'
                '- Nội dung 5: quỹ & danh mục đầu tư. Bao gồm các nội dung: Quỹ đầu tư & Danh mục đầu tư, Quỹ đầu tư, Danh mục đầu tư & Rủi ro tín dụng. Trả về Quỹ & Danh mục đầu tư'
                '- Nội dung 6: pháp lý & quản lý nhà nước. Bao gồm các nội dung: Luật Kinh tế & Luật Thương mại & Luật chứng khoán, Luật chứng khoán, Văn bản hướng dẫn luật, Thanh tra & Quản lý nhà nước. Pháp lý & Quản lý nhà nước'
                'Câu hỏi không liên quan trả về Not Relevant'
            "3. **Trích xuất thực thể (Entity Extraction):**\n"
            "   - **Mã cổ phiếu (Stock ID):** VD: ACB, VCB, TCB...\n"
            "   - **Thời gian (Time Horizon):** Năm (VD: 2025, 2026). Nếu user không nhắc đến, mặc định là **n năm 2026**.\n"
            "   - **Loại tài liệu mục tiêu (Document Type):** \n"
            '     - `income_statement` (Khi hỏi về: doanh thu, lợi nhuận, chi phí, số tuyệt đối).\n'
            '     - `financial_statistics` (Khi hỏi về: ROE, ROA, NIM, NPL, P/E, EPS, tỷ suất, hệ số).\n'
            '     - `all` (Khi hỏi chung chung về tình hình kinh doanh).\n'
            '     - `other` (Khi hỏi về: vấn đề khác).\n'
            "   "
            "\n"
            "3. **Viết lại câu truy vấn (Query Rewriting):**\n"
            "   - Chuyển đổi câu hỏi thông thường của user thành ba câu truy vấn có nghữ nghĩa liên quan tới thị trường chứng khoán.\n"
            "   - Các từ khoá quan trọng xác định entity trong câu hỏi phải được giữ lại trong ba câu truy vấn.\n"
            "   - Kết quả của phần này được ghi vào optimized_search_query trong JSON output.\n"
            "\n"
            "\n"
            "---\n"
            "\n"
            "### Định dạng trả về (JSON Format):\n"
            "CHỈ TRẢ VỀ JSON THUẦN TÚY, KHÔNG sử dụng markdown code block (không có ```json hay ``` bao bọc). Kết quả trả về là tiếng việt không viết hoa.\n"
            "{{\n"
            '  "original_query": "{{user_query}}",\n'
            '  "query_classification": "...",\n'
            '  "content_classification": "...",\n'
            '  "stock_id": "...",\n'
            '  "target_year": "...",\n'
            '  "document_type": "...",\n'
            '  "optimized_search_query": ["...", "...", "..."]\n'
            "}}\n"
        ),
    },
    {
        "role": "user",
        "content": (
            "Phân tích câu hỏi người dùng sau đây:\n\n"
            "Câu hỏi: {user_query}\n"
        ),
    },
]

prompt_template = ChatPromptTemplate.from_messages(preprocess_user_input_template)

chain = prompt_template | llm


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return "".join(text_parts)
    return str(content)


def strip_markdown_json(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1)
    return text.strip()


van_ban_khong_dau = 'Ông Phạm Nhat vuong la ai'

response = chain.invoke({
            "user_query": van_ban_khong_dau
        })

raw_text = extract_text(response.content)
clean_json_text = strip_markdown_json(raw_text)
result = json.loads(clean_json_text)

print(result)

# print(json.dumps(result, indent=2, ensure_ascii=False))

# Step 2: Query qdrant with filter
print("")
main_topic = result["content_classification"]
print(main_topic)
original_query = result["original_query"]
print(original_query)

qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

document_search_service = DocumentSearchService(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="backup_newspaper_embeddded",
    dense_api_key=llm_api_key,
    query_filter={'main_topic': main_topic},
)

dense_hit = document_search_service.simlar_search_with_dense_vector(
    query=original_query,
    limit=20,
)

print(dense_hit)
