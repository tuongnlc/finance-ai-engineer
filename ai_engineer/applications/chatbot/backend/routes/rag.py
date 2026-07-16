from fastapi import APIRouter, Depends

from typing import Annotated

from ai_engineer.applications.chatbot.backend.dependencies import get_document_search_service, get_llm_caller_service_vietnam_language_format_prompt
from ai_engineer.applications.chatbot.backend.schemas.rag import InputVectorSearch, OutputVectorSearch
from ai_engineer.applications.chatbot.service.llm_caller_service import LLMCallerService
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService


router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/get_documents_with_user_query", status_code=200)
async def get_documents_with_user_query(
        request: InputVectorSearch,
        rag_service: Annotated[DocumentSearchService, Depends(get_document_search_service)],
    ) -> OutputVectorSearch:
    query = request.query

    results = rag_service.similar_search_with_hydrid_search(
        query=query,
        limit=20        
    )

    output_documents = rag_service.retrieve_database_with_points(results)

    return OutputVectorSearch(
        results=output_documents,
    )
