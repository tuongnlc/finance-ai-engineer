import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from ai_engineer.frontend.applications.ai_chatbot.integrations.conversation.conversation_client import ConversationClient



class Message(BaseModel):
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ConversationContext(BaseModel):
    conversation_id: uuid.UUID
    user_id: Optional[str] = None
    title: Optional[str] = None
    history: List[Message] = Field(default_factory=list)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationService:
    """
    Orchestrates conversation creation and retrieval for the chatbot UI.
    """

    def __init__(self, client=None) -> None:
        if client is None:
            client = ConversationClient()

        self.client = client

    def start_new_conversation(
        self,
        session_id: uuid.UUID,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        space_id: Optional[str] = None,
        conversation_id: Optional[uuid.UUID] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConversationContext:
        from ai_engineer.applications.chatbot.backend.schemas.conversation import (
            CreateConversationRequest,
        )
        from ai_engineer.helpers.timestamp import create_int_timestamp
        
        conversation_id = conversation_id or uuid.uuid4()
        response = self.client.create_conversation(
            CreateConversationRequest(
                id=conversation_id,
                session_id=session_id,
                title=title,
                user_id=user_id,
                space_id=space_id,
                created_timestamp=create_int_timestamp(),
            )
        )

        return ConversationContext(
            conversation_id=response.id,
            user_id=user_id,
            title=response.title or title,
            history=[],
            context=context or {},
        )

    def get_conversation(
        self,
        conversation_id: uuid.UUID | str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConversationContext:
        response = self.client.get_conversation_by_id(conversation_id)

        return ConversationContext(
            conversation_id=response.id,
            user_id=response.user_id,
            title=response.title,
            context=context or {},
        )
