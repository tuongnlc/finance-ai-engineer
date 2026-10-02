from typing import Annotated
from fastapi import APIRouter, Depends

from ai_engineer.applications.chatbot.backend.dependencies import get_llm_caller_service, get_llm_caller_service_query_understand, get_llm_caller_service_tool_calling, get_llm_caller_service_vietnam_language_format_prompt
from ai_engineer.applications.chatbot.backend.schemas.llm_caller import LLMCallerRequest, LLMCallerResponse, ToolCallingRequest, ToolCallingResponse
from ai_engineer.applications.chatbot.service.agent_caller_service import AgentCallerService
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

@router.post("/query_understand/", status_code=200)
async def query_understand(
        request: LLMCallerRequest,
        llm_service: Annotated[LLMCallerService, Depends(get_llm_caller_service_query_understand)],
    ) -> LLMCallerResponse:
    response = llm_service.call_llm(
        user_question=request.content,
        question_context=None
    )
    return LLMCallerResponse(
        id=request.id,
        response=response
    )

@router.post("/tool_calling/", status_code=200)
async def tool_calling(
        request: ToolCallingRequest,
        llm_service: Annotated[AgentCallerService, Depends(get_llm_caller_service_tool_calling)],
    ) -> ToolCallingResponse:
    response = await llm_service.call_agent(
        preprocessed_query=request.vietnamese_with_diacritics,
    )
    print(response)
    return ToolCallingResponse(
        id=request.id,
        tool_output=response["tool_output"],
        tool_name=response["tool_name"],
        input_message=response["input_message"],
    )
