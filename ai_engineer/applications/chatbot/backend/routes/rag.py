import asyncio

from fastapi import APIRouter

from ai_engineer.applications.chatbot.backend.dependencies import (
    get_rag_collection_names,
    get_document_search_service,
)
from ai_engineer.applications.chatbot.backend.schemas.rag import InputVectorSearch, OutputVectorSearch


router = APIRouter(prefix="/rag", tags=["RAG"])


async def search_collection(collection_name: str, query: str, limit: int = 5) -> list[dict]:
    rag_service = get_document_search_service(collection_name)
    results = await rag_service.retrieve_database_with_user_query(
        query=query,
        limit=limit,
    )
    return results


@router.post("/get_documents_with_user_query", status_code=200)
async def get_documents_with_user_query(
        request: InputVectorSearch,
    ) -> OutputVectorSearch:
    query = request.query

    search_tasks = [
        search_collection(collection_name, query, 5)
        for collection_name in get_rag_collection_names()
    ]
    search_results = await asyncio.gather(*search_tasks)

    output_documents = [
        document
        for result in search_results
        for document in result
    ]

    return OutputVectorSearch(
        results=output_documents,
    )
