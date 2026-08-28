import json
import re
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from polars import Field
from pydantic import BaseModel, RootModel
load_dotenv()

from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm

class TopicAnalysis(BaseModel):
    summary: str 
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 

class TopicAnalysisOutput(RootModel[dict[str, TopicAnalysis]]):
    pass

#extract data for testing
content = """
Công ty Cổ phần Đầu tư và Phát triển Cảng Đình Vũ (MCK: DVP, sàn HoSE) vừa có thông báo về ngày 10/9/2026 là ngày đăng ký cuối cùng để chi trả cổ tức đợt 2 năm 2025. Theo đó, Cảng Đình Vũ sẽ chi trả cổ tức cho cổ đông bằng tiền mặt với tỷ lệ 30%, tức cổ đông sở hữu 1 cổ phiếu sẽ được nhận 3.000 đồng. Với 40 triệu cổ phiếu đang lưu hành, Cảng Đình Vũ sẽ phải chi khoảng 120 tỷ đồng cho đợt trả cổ tức lần này. Ngày thanh toán dự kiến là 30/9/2026. Tính đến ngày 30/6/2026, Công ty Cổ phần Cảng Hải Phòng (MCK: PHP, sàn UPCoM) là công ty mẹ nắm 20,4 triệu cổ phiếu DVP (tỷ lệ 51%) ước tính sẽ thu về 61,2 tỷ đồng cổ tức trong đợt chi trả này; Công ty Cổ phần Vật tư Nông sản sở hữu 7,48 triệu cổ phiếu (tỷ lệ 18,7%), dự kiến cũng sẽ nhận về hơn 22,4 tỷ đồng cổ tức. Trước đó, ngày 29/6/2026, Cảng Đình Vũ đã thực hiện thanh toán cổ tức đợt 1 năm 2025 với tỷ lệ 50%, tức cổ đông sở hữu 1 cổ phiếu sẽ được nhận 5.000 đồng. Như vậy, sau khi hoàn tất đợt chi trả lần này, công ty sẽ hoàn thành phương án cổ tức tỷ lệ 80% cho năm 2025 theo kế hoạch được thông qua tại ĐHĐCĐ thường niên năm 2026. Trong một diễn biến khác, mới đây Cảng Đình Vũ đã công bố Nghị quyết về việc miễn nhiệm chức vụ Chủ tịch HĐQT nhiệm kỳ 2023 - 2028 đối với ông Vũ Tuấn Dương kể từ ngày 16/8/2026 do có đơn xin từ nhiệm. Ở chiều ngược lại, doanh nghiệp quyết định bổ nhiệm ông Lê Hồng Quân- Thành viên HĐQT đảm nhiệm chức vụ Chủ tịch HĐQT nhiệm kỳ 2023 - 2028 kể từ ngày 16/8/2026. Được biết, ông Lê Hồng Quân (SN 1977) có trình độ Thạc sỹ ngành Quản lý hàng hải, Cử nhân Kinh tế và Kỹ sư tin học. Ông Quân được giới thiệu là người đại diện phần vốn của Cảng Hải Phòng tại Cảng Đình Vũ, đồng thời đại diện phần vốn của Tổng Công ty Hàng hải Việt Nam- CTCP tại Cảng Hải Phòng. Bên cạnh đó, ông Quân cũng đang giữ chức vụ Thành viên HĐQT, Tổng Giám đốc, Người đại diện theo pháp luật của Cảng Hải Phòng
"""

main_topic = [
    "quản trị doanh nghiệp",
    "tài chính doanh nghiệp",
    "thị trường & giao dịch"
]

sub_topic = [
    "Giao dịch cổ phiếu trên thị trường",
    "Dự án mới",
    "Chiến lược mới",
    "Thay đổi nhân sự",
    "Huy động vốn & Trái phiếu",
    "Định giá & sự kiện IPO",
    "Thông tin tài chính đáng chú ý",
    "Dự báo tài chính & Tăng trưởng",
    "Vấn đề pháp lý, thanh tra & Kiểm toán",
    "Chia cổ tức & Lịch sự kiện doanh nghiệp",
    "Bối cảnh ngành"
]

stock_mention = ["gas"]

person_mention = [
    "nguyễn thanh bình"
    "phạm văn phong",
    "huỳnh quang hải"
]

from langchain_core.prompts import ChatPromptTemplate

extraction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""Bạn là một trợ lý AI chuyên phân tích và trích xuất thông tin tài chính - doanh nghiệp từ các bài báo, tập trung vào các con số cụ thể. 
Nhiệm vụ của bạn là phân tích đoạn văn bản được cung cấp và trả về kết quả dưới định dạng JSON duy nhất, tuân thủ tuyệt đối cấu trúc yêu cầu.

Hãy tuân thủ các quy tắc sau:
Bước 1: Chọn ra các chủ đề liên quan nhất từ danh sách cho phép bên dưới, việc chọn topic phải liên quan tới doanh nghiệp (tối đa 3 chủ đề), 
Bước 2: Sau đó sử dụng từng chủ đề đó làm key cho một JSON, và viết một đoạn tóm tắt ngắn gọn (khoảng 100 từ) cho từng chủ đề.
Bước 3: Sau đó tiến hành sentiment_analysis cho phần nội dung tóm tắt đó. Nhận một trong 3 giá trị: "Tích cực", "Tiêu cực", "Trung lập".

Danh sách các topic cho phép:
- Chọn giao dịch cổ phiếu trên thị trường. Nếu bài viết liên quan tới việc mua bán cổ phiếu
- Chọn dự án mới. Nếu bài viết đề cập tới các dự án mới của công ty
- Chọn chiến lược mới. Nếu bài viết đề cập tới chiến lược mới của công ty trong mảng kinh doanh giúp tăng vị thế của công ty trong ngành
- Chọn thay đổi nhân sự. Nếu bài viết đề cập tới việc thay đổi nhân sự của công ty
- Chọn huy động vốn & Trái phiếu. Nếu bài viết đề cập tới việc huy động vốn & Trái phiếu của công ty
- Chọn định giá & sự kiện IPO. Nếu bài viết đề cập tới việc định giá & các sự kiện IPO của công ty
- Chọn tài chính công ty. Nếu bài viết đề cập tới các con số tài chính cụ thể như doanh thu, lợi nhuận...
- Chọn dự báo tăng trưởng. Nếu bài viết đề cập tới tăng trưởng của công ty trong tương lai.
- Chọn vấn đề pháp lý, thanh tra & Kiểm toán. Nếu bài viết đề cập tới các vấn đề pháp lý, thanh tra & Kiểm toán của công ty.
- Chọn chia cổ tức & Lịch sự kiện doanh nghiệp. Nếu bài viết đề cập tới các cổ tức & các sự kiện doanh nghiệp của công ty liên quan tới cổ dông.
- Chọn bối cảnh ngành. Nếu bài viết đề cập tới bối cảnh ngành tổng quan như đầu tư công, công nghệ, bất động sản...(không đi vào quá chi tiết) và vị thế của công ty trong ngành.

Đầu ra bắt buộc phải là một đối tượng JSON hợp lệ, không kèm theo bất kỳ văn bản giải thích hay Markdown nào ngoài khối JSON. Theo sát example_output phía trên """
    ),
    (
        "human",
        "Hãy phân tích đoạn văn bản sau:\n\n{text_content}"
    )
])

# call llm 
llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

structured_llm = llm.with_structured_output(TopicAnalysisOutput)

chain = extraction_prompt | structured_llm

response = chain.invoke({
    "text_content": content
})

print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))
