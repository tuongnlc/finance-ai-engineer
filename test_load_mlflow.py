import json
import re
from typing import Literal
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from polars import Field
from pydantic import BaseModel, RootModel
load_dotenv()

from ai_engineer.helpers.prompt.prompt_loading import MLFlowPromptLoading

from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm

class TopicAnalysis(BaseModel):
    summary: str 
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 

class TopicAnalysisOutput(RootModel[dict[str, TopicAnalysis]]):
    pass

parser = PydanticOutputParser(pydantic_object=TopicAnalysisOutput)

prompt = MLFlowPromptLoading(
    prompt_name="topic_summary__business"
).load_and_parse_prompt().partial(
    format_instructions=parser.get_format_instructions()
)

llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

structured_llm = llm.with_structured_output(TopicAnalysisOutput)

chain = prompt | structured_llm

content = """
Công ty Cổ phần Đầu tư và Phát triển Cảng Đình Vũ (MCK: DVP, sàn HoSE) vừa có thông báo về ngày 10/9/2026 là ngày đăng ký cuối cùng để chi trả cổ tức đợt 2 năm 2025. Theo đó, Cảng Đình Vũ sẽ chi trả cổ tức cho cổ đông bằng tiền mặt với tỷ lệ 30%, tức cổ đông sở hữu 1 cổ phiếu sẽ được nhận 3.000 đồng. Với 40 triệu cổ phiếu đang lưu hành, Cảng Đình Vũ sẽ phải chi khoảng 120 tỷ đồng cho đợt trả cổ tức lần này. Ngày thanh toán dự kiến là 30/9/2026. Tính đến ngày 30/6/2026, Công ty Cổ phần Cảng Hải Phòng (MCK: PHP, sàn UPCoM) là công ty mẹ nắm 20,4 triệu cổ phiếu DVP (tỷ lệ 51%) ước tính sẽ thu về 61,2 tỷ đồng cổ tức trong đợt chi trả này; Công ty Cổ phần Vật tư Nông sản sở hữu 7,48 triệu cổ phiếu (tỷ lệ 18,7%), dự kiến cũng sẽ nhận về hơn 22,4 tỷ đồng cổ tức. Trước đó, ngày 29/6/2026, Cảng Đình Vũ đã thực hiện thanh toán cổ tức đợt 1 năm 2025 với tỷ lệ 50%, tức cổ đông sở hữu 1 cổ phiếu sẽ được nhận 5.000 đồng. Như vậy, sau khi hoàn tất đợt chi trả lần này, công ty sẽ hoàn thành phương án cổ tức tỷ lệ 80% cho năm 2025 theo kế hoạch được thông qua tại ĐHĐCĐ thường niên năm 2026. Trong một diễn biến khác, mới đây Cảng Đình Vũ đã công bố Nghị quyết về việc miễn nhiệm chức vụ Chủ tịch HĐQT nhiệm kỳ 2023 - 2028 đối với ông Vũ Tuấn Dương kể từ ngày 16/8/2026 do có đơn xin từ nhiệm. Ở chiều ngược lại, doanh nghiệp quyết định bổ nhiệm ông Lê Hồng Quân- Thành viên HĐQT đảm nhiệm chức vụ Chủ tịch HĐQT nhiệm kỳ 2023 - 2028 kể từ ngày 16/8/2026. Được biết, ông Lê Hồng Quân (SN 1977) có trình độ Thạc sỹ ngành Quản lý hàng hải, Cử nhân Kinh tế và Kỹ sư tin học. Ông Quân được giới thiệu là người đại diện phần vốn của Cảng Hải Phòng tại Cảng Đình Vũ, đồng thời đại diện phần vốn của Tổng Công ty Hàng hải Việt Nam- CTCP tại Cảng Hải Phòng. Bên cạnh đó, ông Quân cũng đang giữ chức vụ Thành viên HĐQT, Tổng Giám đốc, Người đại diện theo pháp luật của Cảng Hải Phòng
"""

response = chain.invoke({
    "text_content": content
})

# print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))