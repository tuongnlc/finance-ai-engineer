from fastapi import APIRouter

from ..schemas.chat import (
    ConversationStatus,
    CreateConversationRequest,
    CreateConversationResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/create_conversation", status_code=201)
async def create_conversation(request: CreateConversationRequest):
    return CreateConversationResponse(**request.model_dump(), status=ConversationStatus.PENDING)
