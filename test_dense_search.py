from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient

from ai_engineer.applications.chatbot.service.rag_service import DocumentSearchService
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm


qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)


#build dense query

van_ban_khong_dau = 'Anh Long chin ngon danh nhau voi ong Nguyen Huu Hy tai cong vien Le Thi Rieng'

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
print("tieng viet co dau")
print(response)


dense_search_service = DocumentSearchService(
    qdrant_client,
    dense_model_name="gemini-embedding-2",
    dense_vector_name="gemini_dense_vector",
    collection_name="newspaper_embedded",
    dense_api_key="",
)

query = response
dense_hit = dense_search_service.simlar_search_with_dense_vector(query)
print(dense_hit)
