

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid
from datetime import date



class ConversationStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Conversation:
    id: uuid.UUID
    created_timestamp: int
    user_id: Optional[str] = None
    space_id: Optional[str] = None
    status: Optional[ConversationStatus] = None
    created_at: date = field(default_factory=date.today)
