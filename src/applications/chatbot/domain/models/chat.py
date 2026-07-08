

from dataclasses import dataclass
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
    user_id: Optional[str] = None
    space_id: Optional[str] = None
    created_timestamp: int 
    status: Optional[ConversationStatus] = None
    created_at: date = date.today()
