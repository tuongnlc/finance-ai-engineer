from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends

from ..schemas.conversation import (
    CreateConversationRequest,
    CreateConversationResponse,
    GetConversationResponse,
    ConversationStatus,
)
from ai_engineer.applications.chatbot.backend.service.conversation_service import ConversationService
from ai_engineer.applications.chatbot.backend.dependencies import get_conversation_service

router = APIRouter(prefix="/conversations", tags=["Conversation"])


@router.post("/", status_code=201)
async def create_conversation(
        request: CreateConversationRequest,
        chat_service: Annotated[ConversationService, Depends(get_conversation_service)],
    ) -> CreateConversationResponse:
    conversation = await chat_service.create_conversation(request)
    return CreateConversationResponse(
        id=conversation.id,
        title=conversation.title,
    )

@router.get("/{conversation_id}", status_code=200)
async def get_conversation(
        conversation_id: UUID,
        conversation_service: Annotated[ConversationService, Depends(get_conversation_service)],
    ) -> GetConversationResponse:
    conversation = await conversation_service.get_by_id(conversation_id)
    return GetConversationResponse(
        id=conversation.id,
        session_id=conversation.session_id,
        title=conversation.title,
        space_id=conversation.space_id,
        user_id=conversation.user_id,
        created_timestamp=conversation.created_timestamp,
        status=conversation.status,
        created_at=conversation.created_at,
    )

@router.get("/", status_code=200)
async def list_conversations(
        conversation_service: Annotated[ConversationService, Depends(get_conversation_service)],
        user_id: Optional[str] = None,
        status: Optional[ConversationStatus] = None,
    ) -> list[GetConversationResponse]:
    conversations = await conversation_service.list_conversations(
        user_id=user_id,
        status=status,
    )
    return [
        GetConversationResponse(
            id=conversation.id,
            session_id=conversation.session_id,
            title=conversation.title,
            space_id=conversation.space_id,
            user_id=conversation.user_id,
            created_timestamp=conversation.created_timestamp,
            status=conversation.status,
            created_at=conversation.created_at,
        )
        for conversation in conversations
    ]
