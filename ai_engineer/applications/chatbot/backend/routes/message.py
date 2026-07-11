from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from ai_engineer.applications.chatbot.backend.dependencies import (
    get_llm_caller_service,
    get_message_service,
)
from ai_engineer.applications.chatbot.backend.schemas.llm_caller import (
    LLMCallerRequest,
    LLMCallerResponse,
)
from ai_engineer.applications.chatbot.backend.schemas.message import (
    CreateMessageRequest,
    CreateMessageResponse,
    GetMessageResponse,
)
from ai_engineer.applications.chatbot.service.llm_caller_service import LLMCallerService
from ai_engineer.applications.chatbot.service.message_service import MessageService

router = APIRouter(prefix="/message", tags=["Message"])

@router.post("/create_message", status_code=201)
async def create_message(
        request: CreateMessageRequest,
        message_service: Annotated[MessageService, Depends(get_message_service)],
    ) -> CreateMessageResponse:
    message = await message_service.create_message(request)
    status = 'PENDING' #Updated later
    return CreateMessageResponse(
        id=message.id,
        space_id=request.space_id,
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        created_timestamp=message.created_timestamp,
        message_url=request.message_url,
        status=status,
        content=request.content,
        created_at=message.created_at,
    )


@router.get("/message/{message_id}", status_code=200)
async def get_message(
        message_id: UUID,
        message_service: Annotated[MessageService, Depends(get_message_service)],
    ) -> GetMessageResponse:
    message = await message_service.get_by_id(message_id)
    return GetMessageResponse(
        id=message.id,
        space_id=message.space_id,
        conversation_id=message.conversation_id,
        user_id=message.user_id,
        created_timestamp=message.created_timestamp,
        status=message.status,

        message_url=message.message_url,
        content=message.content,
        created_at=message.created_at,
    )

@router.get("/conversation/{conversation_id}", status_code=200)
async def get_messages_by_conversation_id(
        conversation_id: UUID,
        message_service: Annotated[MessageService, Depends(get_message_service)],
    ) -> list[GetMessageResponse]:
    messages = await message_service.get_messages_by_conversation_id(conversation_id)
    return messages


@router.post("/chat_with_llm/", status_code=200)
async def chat_with_llm(
        request: LLMCallerRequest,
        llm_service: Annotated[LLMCallerService, Depends(get_llm_caller_service)],
    ) -> LLMCallerResponse:
    response = llm_service.call_llm(
        user_question=request.content,
        question_context=request.question_context,
    )
    return LLMCallerResponse(
        id=request.id,
        response=response
    )
