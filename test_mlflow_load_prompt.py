# import os
# import mlflow
# from dotenv import load_dotenv

# from ai_engineer.shared.llm.create_llm import create_gemini_llm

# load_dotenv()

# llm = create_gemini_llm(
#     api_key=os.getenv("LLM_CHAT_API_KEY_1"),
#     model_name="gemini-3.1-flash-lite",
#     temperature=0,
# )

# # Replace the variables with the actual values

# @mlflow.trace
# def run_prompt():
#     prompt = mlflow.genai.load_prompt("prompts:/finance_agent_2026.test_schema.test_prompt/1")
#     messages = prompt.format(
#         question="What is MLflow?",
#         context="MLflow is a tool for building high-quality agents!"
#     )
#     response = llm.invoke(messages)
#     return response.content

# print(run_prompt())
