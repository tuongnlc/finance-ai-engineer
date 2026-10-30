import os

import mlflow
from dotenv import load_dotenv
from mlflow.genai import search_prompts, load_prompt

load_dotenv()

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "databricks"))
mlflow.set_registry_uri(os.getenv("MLFLOW_REGISTRY_URI", "databricks-uc"))

# 1. Tìm tất cả các prompt hiện có (Unity Catalog yêu cầu filter theo catalog/schema)
prompts = search_prompts("catalog = 'finance_agent_2026' AND schema = 'test_schema'")
for p in prompts:
    print(f"Name: {p.name}")

# 2. Đọc nội dung chi tiết của một prompt cụ thể (hoặc theo alias/version)
# Ví dụ: load_prompt("prompts:/my_financial_summary_prompt/1") 
# hoặc load_prompt("prompts:/catalog.schema.my_prompt@champion")
prompt_obj = load_prompt("prompts:/finance_agent_2026.test_schema.query_understand_prompt/1")
print("Prompt Template:\n", prompt_obj.template)
