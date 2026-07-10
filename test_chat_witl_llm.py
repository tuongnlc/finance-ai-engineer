import os
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ConfigDict

from ai_engineer.applications.chatbot.applications.prompt.prompt_loading import ChatbotPromptLoading
from ai_engineer.applications.chatbot.service.llm_caller_service import LLMCallerService

load_dotenv()

llm_api_key_1 = os.getenv("LLM_CHAT_API_KEY_1")
model = os.getenv("LLM_CHAT_MODEL")
temperature = 0.7

llm = LLMCallerService(
    api_key=llm_api_key_1,
    model_name=model,
    temperature=temperature,
)

# content, response_metadata, tool_calls, invalid_tool_calls, usage_metadata = llm.call_llm(
#     prompt="Hello world!"
# )
# print(content)
# print(response_metadata)
# print(tool_calls)
# print(invalid_tool_calls)
# print(usage_metadata)

# template = [
#     {
#         "role": "system",
#         "content": (
#             "[PERSONA] You are a financial expert. Your expertise spans stock analysis, account management, and financial analysis (including monetary policy and public investment).\n"
#             "[TASK] Communicate with user. Help them answer question about stock market.\n"
#             "[CONTEXT] You operate within a bank like Techcombank or Viettinbank. Think and respond like a financial expert.\n"
#             "[FORMAT] Structure your answer as follows:\n"
#             "Output users in text format\n"
#             "\n"
#             "{format_instructions}\n"
#             "\n"
#         ),
#     },
#     {
#         "role": "user",
#         "content": (
#             "Help me answer this question with the context I send to you. If context is None you can skip this context and focus only about the question.\n\n"
#             "question: {question}\n"
#             "question_context: {question_context}\n"
#             '"""'
#         ),
#     },
# ]


class LLMResponse(BaseModel):
    content: str
   
template = ChatbotPromptLoading().load_and_parse_prompt()

parser = PydanticOutputParser(pydantic_object=LLMResponse)
prompt = template.partial(format_instructions=parser.get_format_instructions())


chain = prompt | llm.llm | parser

result = chain.invoke(
    {
        "question": "Ronaldo la ai!",
        "question_context": None,
    }
)

print(result)