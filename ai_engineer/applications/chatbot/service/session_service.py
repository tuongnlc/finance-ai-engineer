import uuid
from ai_engineer.applications.chatbot.domain.repositories.session import SessionRepository
from ai_engineer.applications.chatbot.domain.models.session import Session


class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self._session_repository = session_repository

    async def create_session(self, request) -> Session:
        conversation_id = request.conversation_id 
        session = Session(
            id = request.id,
            conversation_id = conversation_id,
            created_timestamp = request.created_timestamp,
        )
        return await self._session_repository.create(session)