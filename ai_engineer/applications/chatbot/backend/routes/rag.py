from fastapi import APIRouter, Depends

from typing import Annotated

from ai_engineer.applications.chatbot.backend.dependencies import get_document_search_service
from ai_engineer.applications.chatbot.backend.schemas.rag import InputVectorSearch, OutputVectorSearch
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/get_documents_with_user_query", status_code=200)
async def get_documents_with_user_query(
        request: InputVectorSearch,
        rag_service: Annotated[DocumentSearchService, Depends(get_document_search_service)],
    ) -> OutputVectorSearch:
    collection_name='newspaper_embedded'
    fetch_k=5
    top_k=5
    
    results = rag_service.similar_search_with_query(
        query=request.query,
        collection_name=collection_name,
        fetch_k=fetch_k,
        top_k=top_k,
        with_payload=True,
        with_vectors=False,
    )

    output_documents = rag_service.retrieve_database_with_document_ids(results)

    return OutputVectorSearch(
        results=output_documents,
    )
