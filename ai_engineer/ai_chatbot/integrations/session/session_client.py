from __future__ import annotations

import uuid

import requests
from ai_engineer.helpers.timestamp import create_int_timestamp
from ai_engineer.ai_chatbot.config import get_backend_base_url

from ai_engineer.applications.chatbot.backend.schemas.session import CreateSessionRequest, CreateSessionResponse

class SessionClient:
    """
        Client for Session API

        Create session when user start a new conversation
    """

    def __init__(self, base_url: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or get_backend_base_url()).rstrip("/")
        self.timeout = timeout

    def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        body = request.model_dump(mode="json")

        response = requests.post(
            f"{self.base_url}/session/create_session",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return CreateSessionResponse.model_validate(response.json())
