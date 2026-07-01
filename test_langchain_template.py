from typing import List, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
import json
from pydantic import BaseModel


class StockDetail(BaseModel):
    name: str
    summary: str
    writers_attitude: Literal["Positive", "Negative", "Neutral"]


class NewspaperSummary(BaseModel):
    topic_keywords: List[str]
    overall_sentiment: Literal["Positive", "Negative"]
    stocks: List[str]
    stocks_details: List[StockDetail]
    people: List[str]
    stock_funds: List[str]
    foreign_securities_funds: List[str]
    government_policies: List[str]


parser = PydanticOutputParser(pydantic_object=NewspaperSummary)

# Định nghĩa template chuyên dụng cho bài báo
newspaper_summary_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "[PERSONA] You are a financial expert. Your expertise spans stock analysis, account management, and financial analysis (including monetary policy and public investment).\n"
            "[TASK] Read and understand newspapers, then extract information related to the stock market, market trends, and any stock-related details (company names, related people, etc.).\n"
            "[CONTEXT] You operate within a bank like Techcombank or Viettinbank. Think and respond like a financial expert.\n"
            "[FORMAT] Structure your answer as follows:\n"
            "1. What topic does this newspaper talk about? Return main keywords.\n"
            "2. Overall, is this news negative or positive? Return 'Positive' or 'Negative'.\n"
            "3. What stocks are mentioned? If yes return Name of the stocks seperated by ', '. If no, return 'None'.\n"
            "3.1. For each stock: summary and the writer's attitude.\n"
            "4. Who is mentioned? If yes return Name of the people seperated by ', '. If no, return 'None'.\n"
            "5. What stock funds are mentioned?\n"
            ". Any foreign securities funds are mentioned? If yes, return name of the foreign securities funds.\n If no, return 'None'.\n"
            ". What stock funds are mentioned? If yes return Name of the stock funds seperated by ', '. If no, return 'None'.\n"
            "6. Any new government policy mentioned? If yes, return Name of the policy policy seperated by ', '\n If no, return 'None'.\n"
            "\n"
            "Return ONLY valid JSON (no markdown, no extra text) with this schema:\n"
            "{{\n"
            '  "topic_keywords": ["..."],\n'
            '  "overall_sentiment": "Positive" | "Negative",\n'
            '  "stocks": ["..."],\n'
            '  "stocks_details": [{{"name": "...", "summary": "...", "writers_attitude": "Positive" | "Negative" | "Neutral"}}],\n'
            '  "people": ["..."],\n'
            '  "stock_funds": ["..."],\n'
            '  "foreign_securities_funds": ["..."],\n'
            '  "government_policies": ["..."]\n'
            "}}\n"
            "\n"
            "{format_instructions}\n"

            "--- START OF EXAMPLE ---\n"
            "[EXAMPLE INPUT]\n"
            "Title: Công ty chứng khoán chỉ ra tác động ít được chú ý của Thông tư 25, ảnh hưởng đến nhóm bất động sản, xây dựng\n"
            "Description: Động thái chính sách này được đưa ra trong bối cảnh thanh khoản của hệ thống ngân hàng...\n"
            "Content: Ngày 22/4/2026, Ngân hàng Nhà nước đã chính thức ban hành Thông tư 25/2026...\n\n"
            
            "[EXAMPLE OUTPUT]\n"
            "{{\n"
            '  "topic_keywords": ["Thông tư 25/2026", "Ngân hàng Nhà nước", "tỷ lệ an toàn vốn", "thanh khoản hệ thống"],\n'
            '  "overall_sentiment": "Positive",\n'
            '  "stocks": ["ACBS"],\n'
            '  "stocks_details": [\n'
            '    {{\n'
            '      "name": "ACBS",\n'
            '      "summary": "Khối phân tích đưa ra nhận định chuyên môn về tác động của Thông tư 25/2026 đến hệ thống ngân hàng và chi phí vốn.",\n'
            '      "writers_attitude": "Neutral"\n'
            "    }}\n"
            "  ],\n"
            '  "people": [],\n'
            '  "stock_funds": ["Dragon Capital"],\n'
            '  "foreign_securities_funds": [],\n'
            '  "government_policies": ["Thông tư 25/2026/TT-NHNN sửa đổi Thông tư 22/2019/TT-NHNN"]\n'
            "}}\n"
            "--- END OF EXAMPLE ---"
        ),
        HumanMessagePromptTemplate.from_template(
            "Please summarize the following article:\n\n"
            "Title: {title}\n"
            "Description: {description}\n"
            "Content:\n"
            '"""\n'
            "{content}\n"
            '"""'
        ),
    ]
)

# Giả định dữ liệu bạn cào (crawl) được từ một trang báo
article_data = {
    "title": "Quỹ thuộc Dragon Capital trở thành cổ đông tại MSB, Rox Living đảo chiều muốn mua 100 triệu cp",
    "description": """
        CTCP ROX Living (tiền thân là TNG Realty) là đơn vị thành viên thuộc ROX Group (TNG Holdings đổi tên thành ROX Group).
Các công ty thành viên của Tập đoàn này cũng lần lượt đổi tên, trong đó TNG Realty chuyển thành ROX Living; TNCons Vietnam thành ROX Cons Vietnam; TNG Asset thành ROX Asset; TNG Capital thành ROX Capital… Rox Living là công ty có liên quan đến ông Tạ Ngọc Đa - Thành viên HĐQT MSB.
Nếu giao dịch thành công, Rox Living sẽ nâng tỷ lệ sở hữu tại MSB từ 0.9987% (31.16 triệu cp) lên 4.2038% (131.16 triệu cp).
Người liên quan của VEIL cũng sở hữu hơn 20.5 triệu cp MSB, tương đương 0.66% vốn Ngân hàng.
CTCP Sapphire Invest giảm sở hữu từ hơn 138 triệu cp (4.43%) xuống còn 98.98 triệu cp (3.17%).
    """,
    "content": """
    CTCP Rox Living đăng ký mua 100 triệu cp của Ngân hàng TMCP Hàng hải Việt Nam (HOSE: MSB) trong thời gian từ 29/05-08/06 với lý do đầu tư.

CTCP ROX Living (tiền thân là TNG Realty) là đơn vị thành viên thuộc ROX Group (TNG Holdings đổi tên thành ROX Group). Các công ty thành viên của Tập đoàn này cũng lần lượt đổi tên, trong đó TNG Realty chuyển thành ROX Living; TNCons Vietnam thành ROX Cons Vietnam; TNG Asset thành ROX Asset; TNG Capital thành ROX Capital… Rox Living là công ty có liên quan đến ông Tạ Ngọc Đa - Thành viên HĐQT MSB.

Nếu giao dịch thành công, Rox Living sẽ nâng tỷ lệ sở hữu tại MSB từ 0.9987% (31.16 triệu cp) lên 4.2038% (131.16 triệu cp).

Cổ phiếu MSB đầu phiên 28/05 được giao dịch quanh 15,000 đồng/cp, ước tính theo giá này, Rox Living cần chi khoảng 1,500 tỷ đồng để gia tăng sở hữu.

Chỉ mấy ngày trước đó, Rox Living không bán được cổ phiếu MSB nào trong tổng số đăng ký gần 31.2 triệu cp (0.988%) trong thời gian từ 03-29/04, lý do là điều kiện thị trường chưa phù hợp.

Động thái của Rox Living diễn ra trong bối cảnh MSB vừa công bố danh sách cổ đông sở hữu trên 1% vốn Ngân hàng tính đến ngày 25/05/2026.

Theo danh sách, MSB vừa có thêm cổ đông ngoại mới là Vietnam Enterprise Investments Limited (VEIL) - quỹ thuộc Dragon Capital - với lượng nắm giữ 32.2 triệu cp, tương đương 1.06% vốn. Người liên quan của VEIL cũng sở hữu hơn 20.5 triệu cp MSB, tương đương 0.66% vốn Ngân hàng.

Bên cạnh cổ đông mới công bố, MSB còn ghi nhận biến động sở hữu của một số tổ chức.

Cụ thể, Công ty TNHH Thành phố Công nghệ Xanh Hà Nội giảm sở hữu tại MSB từ 155 triệu cp (4.97%) xuống còn gần 121.98 triệu cp (3.91%). CTCP Sapphire Invest giảm sở hữu từ hơn 138 triệu cp (4.43%) xuống còn 98.98 triệu cp (3.17%).

Trong khi đó, Công ty TNHH Khu nghỉ dưỡng Bãi Dài và CTCP ROX Key Holdings cùng người liên quan vẫn giữ nguyên lượng cổ phiếu nắm giữ.

Các cổ đông lớn khác không thay đổi tỷ lệ sở hữu, gồm VNPT với 6.05% vốn (188.71 triệu cp), CTCP Đầu tư Ricohomes nắm giữ 4.98% (155.38 triệu cp), CTCP Jasper Investment nắm giữ 4.87% (151.88 triệu cp) và quỹ ngoại Buenavista Holdings Limited sở hữu 2.37% vốn (hơn 74 triệu cp).

Trên sàn HOSE, tính đến hết phiên 27/05, giá cổ phiếu MSB đã tăng 21% so với đầu năm, giao dịch quanh 15,000 đồng/cp. Thanh khoản bình quân 9 triệu cp/ngày.

Diễn biến giá cổ phiếu MSB từ đầu năm đến nay

Hàn Đông

FILI

- 08:54 28/05/2026
    """
    }

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key="",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

prompt = newspaper_summary_template.partial(format_instructions=parser.get_format_instructions())
chain = prompt | llm | parser
result = chain.invoke(article_data)
print(json.dumps(result.dict(), ensure_ascii=False, indent=2))
