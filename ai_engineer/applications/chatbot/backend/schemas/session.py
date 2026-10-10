import uuid
from typing import Optional
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = Field(default=None)
    created_timestamp: int

class CreateSessionResponse(BaseModel):
    id: uuid.UUID