from typing import Annotated
from fastapi import APIRouter, Depends
from ..schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
)
from ..dependencies import (
    SessionService,
)
from ai_engineer.applications.chatbot.backend.dependencies import get_session_service


router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/create_session", status_code=201)
async def create_session(
        request: CreateSessionRequest,
        session_service: Annotated[SessionService, Depends(get_session_service)],
    ) -> CreateSessionResponse:
    session = await session_service.create_session(request)
    return CreateSessionResponse(
        id=session.id
    )