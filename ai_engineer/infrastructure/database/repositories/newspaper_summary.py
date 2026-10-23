import uuid
from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ai_engineer.applications.topic_summary.backend.domain.models.newspaper_summary import NewspaperSummary
from ai_engineer.infrastructure.database.orm_models.newspaper_summary import NewspaperSummaryORM


class PostgresNewspaperSummaryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, summary: NewspaperSummary) -> NewspaperSummary:
        summary_orm = self._to_orm(summary)
        self._session.add(summary_orm)
        await self._session.flush()
        await self._session.refresh(summary_orm)
        return self._to_domain(summary_orm)

    async def get_by_id(self, summary_id: uuid.UUID) -> NewspaperSummary | None:
        result = await self._session.execute(
            select(NewspaperSummaryORM).where(NewspaperSummaryORM.id == summary_id)
        )
        summary_orm = result.scalar_one_or_none()
        if summary_orm is None:
            return None
        return self._to_domain(summary_orm)

    async def list(
        self,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> list[NewspaperSummary]:
        stmt = select(NewspaperSummaryORM)
        if min_date is not None:
            stmt = stmt.where(NewspaperSummaryORM.publish_date >= min_date)
        if max_date is not None:
            stmt = stmt.where(NewspaperSummaryORM.publish_date <= max_date)
        result = await self._session.execute(stmt)
        summaries = result.scalars().all()
        return [self._to_domain(summary) for summary in summaries]

    async def delete_by_id(self, summary_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(NewspaperSummaryORM).where(NewspaperSummaryORM.id == summary_id)
        )
        summary_orm = result.scalar_one_or_none()
        if summary_orm is None:
            return
        await self._session.delete(summary_orm)
        await self._session.flush()

    async def update_by_id(
        self,
        summary_id: uuid.UUID,
        is_favorite: Optional[int] = None,
    ) -> NewspaperSummary:
        result = await self._session.execute(
            select(NewspaperSummaryORM).where(NewspaperSummaryORM.id == summary_id)
        )
        summary_orm = result.scalar_one_or_none()
        if summary_orm is None:
            raise ValueError(f"NewspaperSummary with id {summary_id} not found")

        if is_favorite is not None:
            summary_orm.is_favorite = is_favorite

        await self._session.flush()
        await self._session.refresh(summary_orm)
        return self._to_domain(summary_orm)

    def _to_orm(self, summary: NewspaperSummary) -> NewspaperSummaryORM:
        return NewspaperSummaryORM(
            id=summary.id,
            document_id=summary.document_id,
            publish_date=summary.publish_date,
            stocks_mention=summary.stocks_mention,
            person_mention=summary.person_mention,
            newspaper_type=summary.newspaper_type,
            newspaper_summary=summary.newspaper_summary,
            sentiment_analysis=summary.sentiment_analysis,
            circular_and_policy=summary.circular_and_policy,
            legal_documents_and_regulations=summary.legal_documents_and_regulations,
            fund_name=summary.fund_name,
            main_topic=summary.main_topic,
            is_favorite=summary.is_favorite,
        )

    def _to_domain(self, summary: NewspaperSummaryORM) -> NewspaperSummary:
        return NewspaperSummary(
            id=summary.id,
            document_id=summary.document_id,
            publish_date=summary.publish_date,
            stocks_mention=summary.stocks_mention,
            person_mention=summary.person_mention,
            newspaper_type=summary.newspaper_type,
            newspaper_summary=summary.newspaper_summary,
            sentiment_analysis=summary.sentiment_analysis,
            circular_and_policy=summary.circular_and_policy,
            legal_documents_and_regulations=summary.legal_documents_and_regulations,
            fund_name=summary.fund_name,
            main_topic=summary.main_topic,
            is_favorite=summary.is_favorite,
        )
