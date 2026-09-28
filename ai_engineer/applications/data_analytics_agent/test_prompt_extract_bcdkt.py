import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
from ai_engineer.shared.llm.create_llm import create_gemini_llm
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel

# Step 1: Extract data
txt_bctc = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.txt"
file_name = txt_bctc.split('/')[-1]
file_name = file_name.split('.')[0]

with open(txt_bctc, "r") as file:
    content = file.read()

# Step 2: Call LLM to extract data

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
    + "        \"tai_san_ngan_han\": {{\n"
    + "            \"30/6/2026\": \"40.892.259.162.483\",\n"
    + "            \"1/1/2026\": \"36.249.794.729.810\"\n"
    + "        }},\n"
    + "        \"tien_va_cac_khoan_tong_du_tien_tien\": \"38,746.85\",\n"
    + "        \"tien\": \"38,746.85\",\n"
    + "        \"cac_khoan_tong_du_tien_tien\": \"38,746.85\"\n"
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

response_dict = chain_.invoke({"text": content})

response_dict = response_dict.model_dump()


# Step 3: Save as temporary json file
output_dir = Path(txt_bctc).parent
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / f"{file_name}.json"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(response_dict, file, indent=4, ensure_ascii=False)
print(f"Đã lưu kết quả vào: {output_path}")
