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

response = llm.call_llm(
    user_question="Hello world!",
)
print(response)
