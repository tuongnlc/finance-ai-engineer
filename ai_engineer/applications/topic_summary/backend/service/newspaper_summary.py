import uuid
from datetime import date
from typing import Optional
from ai_engineer.applications.topic_summary.backend.domain.repositories.newspaper_summary import NewspaperSummaryRepository
from ai_engineer.applications.topic_summary.backend.domain.models.newspaper_summary import NewspaperSummary


class NewspaperSummaryService:
    def __init__(self, newspaper_summary_repository: NewspaperSummaryRepository):
        self._newspaper_summary_repository = newspaper_summary_repository

    async def create_summary(self, request) -> NewspaperSummary:
        summary = NewspaperSummary(
            id=request.id,
            document_id=request.document_id,
            newspaper_summary=request.newspaper_summary,
            publish_date=request.publish_date,
            stocks_mention=request.stocks_mention,
            person_mention=request.person_mention,
            newspaper_type=request.newspaper_type,
            sentiment_analysis=request.sentiment_analysis,
            circular_and_policy=request.circular_and_policy,
            legal_documents_and_regulations=request.legal_documents_and_regulations,
            fund_name=request.fund_name,
            main_topic=request.main_topic,
        )
        return await self._newspaper_summary_repository.create(summary)

    async def get_by_id(self, summary_id: uuid.UUID) -> NewspaperSummary:
        return await self._newspaper_summary_repository.get_by_id(summary_id)

    async def list_summaries(
        self,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> list[NewspaperSummary]:
        return await self._newspaper_summary_repository.list(min_date=min_date, max_date=max_date)

    async def delete_by_id(self, summary_id: uuid.UUID) -> None:
        return await self._newspaper_summary_repository.delete_by_id(summary_id)
