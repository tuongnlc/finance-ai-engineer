from typing import Protocol
from ai_engineer.applications.chatbot.backend.domain.models.session import Session


class SessionRepository(Protocol):
    async def create(self, session: Session) -> Session:
        pass
