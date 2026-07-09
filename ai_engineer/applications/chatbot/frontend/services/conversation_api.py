import httpx
# from ai_engineer.applications.chatbot.frontend.config import BACKEND_BASE_URL
import uuid
import time



BACKEND_BASE_URL = "http://127.0.0.1:8000/conversation"
#http://127.0.0.1:8000/conversation/conversation/3fa85f64-5717-4562-b3fc-2c963f66afa6
class ConversationApi:
    """
        Communicate directly with back-end service
    """
    async def create_conversation(self, content: str, user_id: str | None, space_id: str | None):
        payload = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "space_id": space_id,
            "created_timestamp": int(time.time()),
            "content": content,
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{BACKEND_BASE_URL}/create_conversation",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_conversation_by_id(self, conversation_id: uuid.UUID | str):
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                resp = await client.get(
                    f"{BACKEND_BASE_URL}/conversation/{conversation_id}",
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError:
                return None
