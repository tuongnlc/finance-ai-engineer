from typing import Protocol, Optional
import uuid
from datetime import date
from ai_engineer.applications.chatbot.domain.models.newspaper_summary import NewspaperSummary


class NewspaperSummaryRepository(Protocol):
    async def create(self, summary: NewspaperSummary) -> NewspaperSummary:
        pass

    async def get_by_id(self, summary_id: uuid.UUID) -> NewspaperSummary:
        pass

    async def list(
        self,
        publish_date: Optional[date] = None,
    ) -> list[NewspaperSummary]:
        pass

    async def delete_by_id(self, summary_id: uuid.UUID) -> None:
        pass