import httpx
import uuid


BACKEND_BASE_URL_CHAT = "http://127.0.0.1:8000/ai_chat/chat_with_llm"
BACKEND_BASE_URL_FORMAT_TEXT = "http://127.0.0.1:8000/ai_chat/normalize_vietnam_sentence"

class ChatWithLLMApi:
    """
        Communicate directly with back-end service
    """
    async def chat_with_llm(self, 
        id: uuid.UUID,
        user_question: str,
        question_context: str | None = None,
    ):
        payload = {
            "id": str(id),
            "content": user_question,
            "question_context": question_context,
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{BACKEND_BASE_URL_CHAT}",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()


class VietnamTextFormatAPI:
    """
        Format text to follow Vietnam's grammar
    """
    async def format_text(self, 
        id: uuid.UUID,
        user_question: str,
        question_context: str | None = None,
    ):
        payload = {
            "id": str(id),
            "content": user_question,
            "question_context": question_context,
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{BACKEND_BASE_URL_FORMAT_TEXT}",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()