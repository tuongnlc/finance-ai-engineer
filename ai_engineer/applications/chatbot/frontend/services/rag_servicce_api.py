import httpx
import uuid


BACKEND_BASE_URL = "http://127.0.0.1:8000/rag/get_documents_with_user_query"


class RAGServiceApi:
    """
        Communicate directly with back-end service
    """
    async def get_documents_with_user_query(self, 
        user_query: str,
    ):
        payload = {
            "query": user_query,
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                f"{BACKEND_BASE_URL}",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
