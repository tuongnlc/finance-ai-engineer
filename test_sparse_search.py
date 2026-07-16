from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient

from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_llm


qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)


#build dense query

van_ban_khong_dau = 'Hello'

llm = create_gemini_llm(
    api_key="",
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

prompt_template = ChatPromptTemplate.from_messages([
        (
            "system", """You are a machine translate machine. Your job is convert from Vietnamese without diacritics to Vietnamese with diacritics. 
                        You don't need to add any punctuation marks.
                        If user input Vietnamese with diacritics do nothing. return original text.
                        If user input is not Vietnamese, return original text.
                        """
        ),
        ("user", "{text}")
    ])

chain = prompt_template | llm


response = chain.invoke({
            "text": van_ban_khong_dau
        })

response = response.content[0].get("text")
print(response)

#token nization and create sparse vector
from underthesea import word_tokenize
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient, models

tokens = word_tokenize(response, format="text")


sparse_search_service = DocumentSearchService(
    qdrant_client,
    sparse_model_name="Qdrant/bm25",
    sparse_vector_name="bm25_sparse",
    collection_name="newspaper_embedded",
)

# sparse

query = response
sparse_hit = sparse_search_service.simlar_search_with_sparse_vector(response)
# print(sparse_hit)

document_ids = sparse_search_service.retrieve_database_with_document_ids(sparse_hit)
print(document_ids)
