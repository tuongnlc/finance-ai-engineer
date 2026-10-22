from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ai_engineer.infrastructure.database.repositories.newspaper_summary import PostgresNewspaperSummaryRepository
from ai_engineer.infrastructure.database.session import get_session
from ai_engineer.applications.topic_summary.backend.service.newspaper_summary import NewspaperSummaryService


def get_newspaper_summary_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NewspaperSummaryService:
    newspaper_summary_repository = PostgresNewspaperSummaryRepository(session)
    return NewspaperSummaryService(newspaper_summary_repository)