from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Khởi tạo model Gemini (mặc định hiện tại thường dùng gemini-1.5-flash hoặc pro)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key="",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Gửi tin nhắn và nhận phản hồi
messages = [
    SystemMessage(content="Bạn là một chuyên gia phân tích dữ liệu tài chính tài ba."),
    HumanMessage(content="Giải thích ngắn gọn ý nghĩa của thanh khoản trong thị trường chứng khoán."),
]

ai_msg = llm.invoke(messages)
print(ai_msg.content)
