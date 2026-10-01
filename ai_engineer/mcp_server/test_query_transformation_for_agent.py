import json
import re
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# from ai_engineer.helpers.prompt.prompt_registry import prompt_register
load_dotenv()

from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

prompt_register = PromptRegister()

prompt_template = prompt_register.load_and_parse_prompt('query_preprocessing_prompt')

chain = prompt_template | llm


van_ban_khong_dau = 'Loi nhuan cua ngan hang ACB ngay 10 thang 9'

van_ban_khong_dau = 'Kha Banh la ai'


response = chain.invoke({
            "user_query": van_ban_khong_dau
        })

print(response.content[0].get("text"))