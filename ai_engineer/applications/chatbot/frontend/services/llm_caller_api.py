import httpx
import uuid
import time


BACKEND_BASE_URL = "http://127.0.0.1:8000/message/chat_with_llm"

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
                f"{BACKEND_BASE_URL}",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
