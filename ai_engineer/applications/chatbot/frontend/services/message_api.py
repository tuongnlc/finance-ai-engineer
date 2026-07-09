import httpx
import uuid
import time



BACKEND_BASE_URL = "http://127.0.0.1:8000/message/create_message"
class MessageApi:
    """
        Communicate directly with back-end service
    """
    async def create_message(self, 
        space_id: str,
        conversation_id: uuid.UUID,
        user_id: str | None,
        content_type: str | None,
        message_url: str | None,
        status: str | None,
        content: str | None,
        attachments: str | None,
    ):
        payload = {
            "id": str(uuid.uuid4()),
            "space_id": space_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "content_type": content_type,
            "message_url": message_url,
            "status": status,
            "content": content,
            "created_timestamp": int(time.time()),
            "attachments": attachments,
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{BACKEND_BASE_URL}",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
