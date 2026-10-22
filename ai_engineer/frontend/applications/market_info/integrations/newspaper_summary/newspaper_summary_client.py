from __future__ import annotations

from datetime import date
from typing import Optional
import requests
from ai_engineer.frontend.config import get_backend_base_url
from ai_engineer.applications.topic_summary.backend.schemas.newspaper_summary import (
    GetNewspaperSummaryResponse,
)


class NewspaperSummaryClient:
    """
        Client for Newspaper Summary API

        List newspaper summaries within a date range
    """

    def __init__(self, base_url: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or get_backend_base_url()).rstrip("/")
        self.timeout = timeout

    def list_summaries(
        self,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> list[GetNewspaperSummaryResponse]:
        response = requests.get(
            f"{self.base_url}/newspaper-summary/",
            params={
                "min_date": min_date,
                "max_date": max_date,
            },
            headers={
                "accept": "*/*",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return [
            GetNewspaperSummaryResponse.model_validate(item)
            for item in response.json()
        ]
