from langchain_core.prompts import ChatPromptTemplate
import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from ai_engineer.shared.llm.create_llm import create_gemini_llm
from langchain_core.output_parsers import PydanticOutputParser


from pydantic import BaseModel

# Step 1: Read txt or json file. Get content 
txt_urls_thong_tin_chung = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/thong_tin_chung.txt"

with open(txt_urls_thong_tin_chung, "r") as file:
    content = file.read()

file_name = txt_urls_thong_tin_chung.split('/')[-1]
file_name = file_name.split('.')[0]
print(file_name)

# Step 3: Do extraction
if file_name == "thong_tin_chung":
    content = content


class OutputContentGeneralInformation(BaseModel):
    hoi_dong_quan_tri: list
    ban_dieu_hanh: list

parser = PydanticOutputParser(pydantic_object=OutputContentGeneralInformation)

prompt = ChatPromptTemplate.from_template(
    (
    "[PERSONA] Bạn là một chuyên gia tài chính, hiểu rõ các thuật ngữ tài chính, kinh tế.\n"
    + "[TASK]Tôi sẽ gửi cho bạn một c. Nhiệm vụ của bạn là đọc đoạn văn nhỏ được tách ra từ báo cáo tài chính. Và tiến hành những điều sau.\n"
    + "Cho tôi biết hội đồng quản trị của công ty gồm những ai."
    + "Cho tôi biết ban điều hành gồm những ai"
    + "--- START OF EXAMPLE ---\n"
    + "[EXAMPLE INPUT]\n"
    + "\n"
    + "\n"
    + "[EXAMPLE OUTPUT]\n"
    + "{{\n"
    + "    \"hoi_dong_quan_tri\": [\"A\", \"B\", \"C\"],\n"
    + "    \"ban_dieu_hanh\": [\"D\", \"E\", \"F\"]\n"
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
structured_llm = llm.with_structured_output(OutputContentGeneralInformation)

chain_ = prompt | structured_llm


response = chain_.invoke({"text": content})
response_dict = response.model_dump()
print(response_dict)

# Save as temporary json
output_dir = Path(txt_urls_thong_tin_chung).parent
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / f"{file_name}.json"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(response_dict, file, indent=4, ensure_ascii=False)
print(f"Đã lưu kết quả vào: {output_path}")

