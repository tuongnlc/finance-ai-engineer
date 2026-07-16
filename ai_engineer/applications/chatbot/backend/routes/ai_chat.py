from typing import Annotated
from fastapi import APIRouter, Depends

from ai_engineer.applications.chatbot.backend.dependencies import get_llm_caller_service, get_llm_caller_service_vietnam_language_format_prompt
from ai_engineer.applications.chatbot.backend.schemas.llm_caller import LLMCallerRequest, LLMCallerResponse, LLMCallerWithoutContextRequest
from ai_engineer.applications.chatbot.service.llm_caller_service import LLMCallerService


router = APIRouter(prefix="/ai_chat", tags=["AI Chat"])


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

@router.post("/normalize_vietnam_sentence/", status_code=200)
async def normalize_vietnam_sentence(
        request: LLMCallerRequest,
        llm_service: Annotated[LLMCallerService, Depends(get_llm_caller_service_vietnam_language_format_prompt)],
    ) -> LLMCallerResponse:
    response = llm_service.call_llm(
        user_question=request.content,
        question_context=None
    )
    return LLMCallerResponse(
        id=request.id,
        response=response
    )