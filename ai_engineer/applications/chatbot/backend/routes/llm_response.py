from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from ai_engineer.applications.chatbot.backend.schemas.llm_response import LLMResponseRequest, LLMResponseResponse
from ai_engineer.applications.chatbot.service.llm_response_service import LLMResponseService
from ai_engineer.applications.chatbot.backend.dependencies import get_llm_response_service

router = APIRouter(prefix="/llm_response", tags=["LLM Response"])

@router.post("/create_llm_response", status_code=201)
async def create_llm_response(
        request: LLMResponseRequest,
        llm_response_service: Annotated[LLMResponseService, Depends(get_llm_response_service)],
    ) -> LLMResponseResponse:
    llm_response = await llm_response_service.create(request)
    return LLMResponseResponse(
        id=llm_response.id,
        message_id=llm_response.message_id,
        conversation_id=llm_response.conversation_id,
        llm_response=llm_response.llm_response,
        content_type=llm_response.content_type,
        attachments=llm_response.attachments,
        created_at=llm_response.created_at,
    )


@router.get("/llm_response/{llm_response_id}", status_code=200)
async def get_llm_response(
        llm_response_id: UUID,
        llm_response_service: Annotated[LLMResponseService, Depends(get_llm_response_service)],
    ) -> LLMResponseResponse:
    llm_response = await llm_response_service.get_by_id(llm_response_id)
    return LLMResponseResponse(
        id=llm_response.id,
        message_id=llm_response.message_id,
        conversation_id=llm_response.conversation_id,
        llm_response=llm_response.llm_response,
        content_type=llm_response.content_type,
        attachments=llm_response.attachments,
        created_at=llm_response.created_at,
    )

@router.get("/conversation/{conversation_id}", status_code=200)
async def get_llm_responses_by_conversation_id(
        conversation_id: UUID,
        llm_response_service: Annotated[LLMResponseService, Depends(get_llm_response_service)],
    ) -> list[LLMResponseResponse]:
    return await llm_response_service.get_responses_by_conversation_id(conversation_id)
