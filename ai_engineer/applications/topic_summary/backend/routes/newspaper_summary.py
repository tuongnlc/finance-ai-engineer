from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from ai_engineer.applications.topic_summary.backend.dependencies import (
    get_newspaper_summary_service,
)

from ai_engineer.applications.topic_summary.backend.schemas.newspaper_summary import (
    CreateNewspaperSummaryRequest,
    CreateNewspaperSummaryResponse,
    GetNewspaperSummaryResponse,
)
from ai_engineer.applications.topic_summary.backend.service.newspaper_summary import (
    NewspaperSummaryService,
)

router = APIRouter(prefix="/newspaper-summary", tags=["NewspaperSummary"])


@router.post("/", status_code=201)
async def create_newspaper_summary(
        request: CreateNewspaperSummaryRequest,
        newspaper_summary_service: Annotated[NewspaperSummaryService, Depends(get_newspaper_summary_service)],
    ) -> CreateNewspaperSummaryResponse:
    summary = await newspaper_summary_service.create_summary(request)
    return CreateNewspaperSummaryResponse(
        id=summary.id,
        document_id=summary.document_id,
    )


@router.get("/{summary_id}", status_code=200)
async def get_newspaper_summary(
        summary_id: UUID,
        newspaper_summary_service: Annotated[NewspaperSummaryService, Depends(get_newspaper_summary_service)],
    ) -> GetNewspaperSummaryResponse:
    summary = await newspaper_summary_service.get_by_id(summary_id)
    return GetNewspaperSummaryResponse(
        id=summary.id,
        document_id=summary.document_id,
        newspaper_summary=summary.newspaper_summary,
        publish_date=summary.publish_date,
        stocks_mention=summary.stocks_mention,
        person_mention=summary.person_mention,
        newspaper_type=summary.newspaper_type,
        sentiment_analysis=summary.sentiment_analysis,
        circular_and_policy=summary.circular_and_policy,
        legal_documents_and_regulations=summary.legal_documents_and_regulations,
        fund_name=summary.fund_name,
        main_topic=summary.main_topic,
        is_favorite=summary.is_favorite,
    )

@router.get("/", status_code=200)
async def list_newspaper_summaries(
        newspaper_summary_service: Annotated[NewspaperSummaryService, Depends(get_newspaper_summary_service)],
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> list[GetNewspaperSummaryResponse]:
    summaries = await newspaper_summary_service.list_summaries(min_date=min_date, max_date=max_date)
    return [
        GetNewspaperSummaryResponse(
            id=summary.id,
            is_favorite=summary.is_favorite,
            document_id=summary.document_id,
            newspaper_summary=summary.newspaper_summary,
            publish_date=summary.publish_date,
            stocks_mention=summary.stocks_mention,
            person_mention=summary.person_mention,
            newspaper_type=summary.newspaper_type,
            sentiment_analysis=summary.sentiment_analysis,
            circular_and_policy=summary.circular_and_policy,
            legal_documents_and_regulations=summary.legal_documents_and_regulations,
            fund_name=summary.fund_name,
            main_topic=summary.main_topic,
        )
        for summary in summaries
    ]


@router.delete("/{summary_id}", status_code=204)
async def delete_newspaper_summary(
        summary_id: UUID,
        newspaper_summary_service: Annotated[NewspaperSummaryService, Depends(get_newspaper_summary_service)],
    ) -> None:
    await newspaper_summary_service.delete_by_id(summary_id)
