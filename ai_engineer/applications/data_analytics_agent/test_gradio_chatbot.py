import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import gradio as gr

from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm
import os

from dotenv import load_dotenv

load_dotenv()


llm_api_key = os.getenv("LLM_CHAT_API_KEY_1")

llm = create_gemini_llm(
    api_key=llm_api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

url = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.json"
with open(url, "r") as file:
    data = json.load(file)

    financial_data = data["financial_data"]

def call_llm(message, history):
    context = financial_data

    message = f"""
    with this context: {context}
    help me answer the question: {message}
    """

    return llm.invoke(message).content

# Tạo giao diện Chatbot đơn giản
demo = gr.ChatInterface(
    fn=call_llm, 
    title="Chatbot Đơn Giản", 
    description="Nhập tin nhắn bất kỳ để bắt đầu trò chuyện."
)

if __name__ == "__main__":
    demo.launch()