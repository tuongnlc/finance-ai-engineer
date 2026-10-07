import uuid
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_timestamp: int

class CreateSessionResponse(BaseModel):
    id: uuid.UUID