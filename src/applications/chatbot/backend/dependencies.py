from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.applications.chatbot.app.conversation_service import ConversationService
from src.infrastructure.database.repositories.conversation import PostgresConversationRepository
from src.infrastructure.database.session import get_session


def get_conversation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationService:
    conversation_repository = PostgresConversationRepository(session)
    return ConversationService(conversation_repository)
