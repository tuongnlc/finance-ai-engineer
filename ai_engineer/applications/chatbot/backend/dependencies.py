import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engineer.applications.chatbot.service.conversation_service import ConversationService
from ai_engineer.applications.chatbot.service.llm_caller_service import LLMCallerService
from ai_engineer.applications.chatbot.service.llm_response_service import LLMResponseService
from ai_engineer.applications.chatbot.service.message_service import MessageService
from ai_engineer.infrastructure.database.repositories.conversation import PostgresConversationRepository
from ai_engineer.infrastructure.database.repositories.llm_response import PostgresLLMResponseRepository
from ai_engineer.infrastructure.database.repositories.message import PostgresMessageRepository
from ai_engineer.infrastructure.database.session import get_session


def get_conversation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationService:
    conversation_repository = PostgresConversationRepository(session)
    return ConversationService(conversation_repository)


def get_message_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageService:
    message_repository = PostgresMessageRepository(session)
    return MessageService(message_repository)


def get_llm_response_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LLMResponseService:
    llm_response_repository = PostgresLLMResponseRepository(session)
    return LLMResponseService(llm_response_repository)


@lru_cache
def get_llm_caller_service() -> LLMCallerService:
    return LLMCallerService(
        api_key=os.getenv("LLM_CHAT_API_KEY_1"),
        model_name=os.getenv("LLM_CHAT_MODEL"),
        temperature=0.7,
    )
