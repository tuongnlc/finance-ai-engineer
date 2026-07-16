from qdrant_client import QdrantClient
from ai_engineer.applications.chatbot.applications.prompt.prompt_loading import ChatbotPromptLoading
from ai_engineer.applications.chatbot.service.llm_caller_service import LLMCallerService
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService

prompt_tempalte = ChatbotPromptLoading(prompt_name='vietnam_language_format_prompt').load_and_parse_prompt()
# print(prompt_tempalte)

llm = LLMCallerService(
    api_key="",
    model_name="gemini-3.1-flash-lite",
    temperature=0,
    prompt_name='vietnam_language_format_prompt',
)

response = llm.call_llm(
    user_question="Nguoi anh em bao nhieu tuoi",
)
# print(response.co)
response = response[0].get("text")
print(response)

qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

document_search_service = DocumentSearchService(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="newspaper_embedded",
    dense_api_key="",
)
hydrid_hit = document_search_service.similar_search_with_hydrid_search(
    query=response,
    limit=20
)

print(hydrid_hit)

output_documents = document_search_service.retrieve_database_with_points(hydrid_hit)
print(output_documents)
