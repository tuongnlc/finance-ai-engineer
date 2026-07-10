
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional
import uuid


@dataclass
class LLMResponse:
    id: uuid.UUID
    message_id: uuid.UUID
    conversation_id: uuid.UUID
    llm_response: str
    content_type: str = "TEXT"
    attachments: Optional[list[dict[str, Any]]] = None
    created_at: date = field(default_factory=date.today)
    
