# load_dotenv()
from dotenv import load_dotenv

import os

from qdrant_client import QdrantClient, models
from ai_engineer.shared.llm.create_llm import create_gemini_embedding, create_gemini_llm
from langchain_core.prompts import ChatPromptTemplate
from underthesea import word_tokenize
from fastembed import SparseTextEmbedding


load_dotenv()

api_key = os.getenv("LLM_CHAT_API_KEY_2")

input_test = "Messi lam o ngan hang ACB"

qdrant_client = QdrantClient(
    url="http://localhost:6333", timeout=600
)


#The process is 
# Step 1: Generate vietnamese text from query
# Step 2: Calculate the sparse vector of the text
# Step 3: Calculate the dense vector of the text
# Step 4: Calculate sparse vector similarity score
# Step 5: Calculate dense vector similarity score
# Step 6: Calculate hydrid vector similarity score

# Step 1: Generate vietnamese text from query
llm = create_gemini_llm(
    api_key="",
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)


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
            "text": input_test
        })

response = response.content[0].get("text")

# Step 2: Calculate the sparse vector of the text
tokens = word_tokenize(response, format="text")
bm25_model = SparseTextEmbedding(model_name="Qdrant/bm25",  disable_stemmer=True)
sparse_vector = next(bm25_model.embed([tokens]))
sparse_vector_indices, sparse_vector_values = sparse_vector.indices, sparse_vector.valuess

# Step 3: Calculate the dense vector of the text
embedding_llmn = create_gemini_embedding(
    model_name="gemini-embedding-2",
    api_key="",
    output_dimensionality=768,
)
dense_vector = embedding_llmn.embed_query(response)

# Step 4: Calculate sparse vector similarity score
sparse_hits = qdrant_client.query_points(
    collection_name="newspaper_embedded",
    query=models.SparseVector(
        indices=sparse_vector.indices,
        values=sparse_vector.values
    ),
    using="bm25_sparse",
    limit=20,
    with_payload=False,
)

# Step 5: Calculate dense vector similarity score
dense_hits =  qdrant_client.query_points(
    collection_name="newspaper_embedded",
    query=dense_vector,
    using="gemini_dense_vector",
    limit=20,
    with_payload=False,
)

# Step 6: Calculate hydrid vector similarity score
hybrid_hits = qdrant_client.query_points(
    collection_name="newspaper_embedded",
    prefetch=[
        # Fetch top 20 using dense semantic search
        models.Prefetch(
            query=dense_vector,
            using="gemini_dense_vector",
            limit=20,
            # score_threshold=0.7,
        ),
        # Fetch top 20 using sparse keyword search
        models.Prefetch(
            query=models.SparseVector(
                indices=sparse_vector.indices,
                values=sparse_vector.values
            ),
            using="bm25_sparse",
            limit=20,
            # score_threshold=15,
        )
    ],
    # Blend the two lists into a final top 10 using RRF
    query=models.FusionQuery(
        fusion=models.Fusion.RRF
    ),
    limit=10,
    # score_threshold=0.3
)