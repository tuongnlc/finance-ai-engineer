# from qdrant_client.models import , Fusion

#Convert Vietnamese without diacritics to Vietnamese with diacritics
from qdrant_client import QdrantClient, models
from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm

# van_ban_khong_dau = "chuyen tu tieng viet khong dau thanh co dau"
# van_ban_khong_dau = '[Python] Chuyển tên file tiếng Việt có dấu thành không dấu'
# van_ban_khong_dau = 'Deo hieu sao Long chin ngon lai noi tieng'
van_ban_khong_dau = 'So nha 419/15 Chu Van An co ai o khong'

llm = create_gemini_llm(
    api_key="",
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

from langchain_core.prompts import ChatPromptTemplate

# llm.invoke("Chuyen tu tieng viet thanh co dau")

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
print("tieng viet co dau")
print(response)

#token nization and create sparse vector
from underthesea import word_tokenize
from fastembed import SparseTextEmbedding

# tokens = word_tokenize(response, format="text")
# # print(tokens)
# bm25_model = SparseTextEmbedding(model_name="Qdrant/bm25",  disable_stemmer=True)
# sparse_vector = next(bm25_model.embed([tokens]))
# # print(sparse_vector)
# print(sparse_vector.indices)
# print(sparse_vector.values)


# # create vector embedding
# embedding_llmn = create_gemini_embedding(
#     model_name="gemini-embedding-2",
#     api_key="",
#     output_dimensionality=768,
# )
# dense_vector = embedding_llmn.embed_query(response)
# print(dense_vector)


# query qdrant db
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

# print(hydrid_hit)
output_documents = document_search_service.retrieve_database_with_points(hydrid_hit)
print(output_documents)
