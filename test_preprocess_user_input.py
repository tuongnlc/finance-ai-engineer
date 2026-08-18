from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

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
            "Nhiệm vụ của bạn là chuyển user query thành tiếng việt có dấu, sau đó phân tích input của người dùng để trích xuất các thực thể và định hướng truy xuất dữ liệu.\n"
            "\n"
            "---\n"
            "\n"
            "### Nhiệm vụ khi nhận input của user:\n"
            "1. **Trích xuất thực thể (Entity Extraction):**\n"
            "   - **Mã cổ phiếu (Stock ID):** VD: ACB, VCB, TCB...\n"
            "   - **Thời gian (Time Horizon):** Năm (VD: 2025, 2026), Quý (VD: Q1, Q2, Q4). Nếu user không nhắc đến, mặc định là **kỳ gần nhất của năm 2026**.\n"
            "   - **Loại tài liệu mục tiêu (Document Type):** \n"
            '     - `income_statement` (Khi hỏi về: doanh thu, lợi nhuận, chi phí, số tuyệt đối).\n'
            '     - `financial_statistics` (Khi hỏi về: ROE, ROA, NIM, NPL, P/E, EPS, tỷ suất, hệ số).\n'
            '     - `all` (Khi hỏi chung chung về tình hình kinh doanh).\n'
            '     - `other` (Khi hỏi về: vấn đề khác).\n'
            "\n"
            "2. **Viết lại câu truy vấn (Query Rewriting):**\n"
            "   - Chuyển đổi câu hỏi thông thường của user thành dạng truy vấn chuẩn hóa cho Vector DB / Keyword Search.\n"
            "\n"
            "---\n"
            "\n"
            "### Định dạng trả về (JSON Format):\n"
            "{{\n"
            '  "original_query": "{{user_query}}",\n'
            '  "stock_id": "...",\n'
            '  "target_year": "...",\n'
            '  "document_type": "...",\n'
            '  "optimized_search_query": "..."\n'
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


van_ban_khong_dau = 'Ong Pham Nhat Vuong La Ai'

response = chain.invoke({
            "user_query": van_ban_khong_dau
        })

print(response.content)