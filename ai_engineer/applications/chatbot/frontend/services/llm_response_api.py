import httpx
import uuid
from datetime import date

MESSAGE_BASE_URL = "http://127.0.0.1:8000/llm_response"  

class LLMResponseApi:
    """
        Communicate directly with back-end service
    """
    async def create_llm_response(self, 
        id: uuid.UUID | str,
        message_id: uuid.UUID | str,
        conversation_id: uuid.UUID | str,
        llm_response: str,
        content_type: str = "TEXT",
        attachments = None,
        created_at: date = date.today(),
    ):
        payload = {
            "id": str(id),
            "message_id": str(message_id),
            "conversation_id": str(conversation_id),
            "llm_response": llm_response,
            "content_type": content_type,
            "attachments": attachments,
            "created_at": created_at.isoformat(),
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{MESSAGE_BASE_URL}/create_llm_response",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_llm_responses_by_conversation_id(self, 
        conversation_id: uuid.UUID | str,
    ):
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(
                f"{MESSAGE_BASE_URL}/conversation/{conversation_id}",
            )
            resp.raise_for_status()
            return resp.json()
