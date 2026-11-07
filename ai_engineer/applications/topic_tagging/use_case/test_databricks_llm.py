# from openai import OpenAI
# import os

# # How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# # Alternatively in a Databricks notebook you can use this:
# # DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# client = OpenAI(
#     api_key=DATABRICKS_TOKEN,
#     base_url="https://dbc-a4257ab8-9fcb.cloud.databricks.com/ai-gateway/mlflow/v1"
# )

# response = client.chat.completions.create(
#     model="test_ocr.test_ocr.test_serving_model",
#     messages=[
#         {
#             "role": "user",
#             "content": "What is an LLM agent?"
#         }
#     ],
#     max_tokens=5000
# )

# print(response.choices[0].message.content)