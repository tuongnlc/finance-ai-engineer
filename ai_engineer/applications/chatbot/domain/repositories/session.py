from typing import Protocol
import uuid

from ai_engineer.applications.chatbot.domain.models.session import Session


class SessionRepository(Protocol):
    async def create(self, session: Session) -> Session:
        pass
