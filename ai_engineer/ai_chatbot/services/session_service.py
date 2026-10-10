from __future__ import annotations

import uuid

from ai_engineer.ai_chatbot.integrations.session.session_client import SessionClient
from ai_engineer.applications.chatbot.backend.schemas.session import CreateSessionRequest
from ai_engineer.helpers.timestamp import create_int_timestamp
from pydantic import BaseModel


class SessionContext(BaseModel):
    session_id: uuid.UUID
    # conversation_id: uuid.UUID | None = None

class SessionService:
    """
    Orchestrates session creation for the chatbot UI.

    This service is responsible for generating identifiers needed by the
    frontend flow, calling the backend session API, and returning a compact
    context object that pages can store in `st.session_state`.
    """

    def __init__(self, client: SessionClient | None = None) -> None:
        self.client = client or SessionClient()

    def start_new_session(
        self,
        conversation_id: uuid.UUID | None = None,
        session_id: uuid.UUID | None = None,
    ) -> SessionContext:
        conversation_id = conversation_id 
        session_id = session_id or uuid.uuid4()

        response = self.client.create_session(
            CreateSessionRequest(
                id=session_id,
                conversation_id=conversation_id,
                created_timestamp=create_int_timestamp(),
            )
        )

        return SessionContext(
            session_id=response.id,
            conversation_id=conversation_id,
        )
