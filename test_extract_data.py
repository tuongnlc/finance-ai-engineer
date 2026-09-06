from ai_engineer.applications.topic_tagging.use_case.topic_tagging import TopicTaggingUseCase
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
# ReplaceCharInColumn
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.shared.data_pipeline.transform.columns import ReplaceCharInColumn, SelectColumns
import polars as pl

# TopicTaggingUseCase

# Step 1: Extract newspaper data from Qdrant collection
newspaper_extractor = QdrantExtractorWithPayloadFilter(
    # qdrant_url="localhost:6333",
    qdrant_url="http://localhost:6333", #when run in docker composer
    collection_name="newspaper",
    payload_filter={
        "is_topic_tagging": 0
    },
    with_vectors=False,
)

df_ = newspaper_extractor.extract()
print(len(df_))
# extracted_ids = df_.select(["id"])

# # extracted_ids_format = ReplaceCharInColumn("id", "-", "").transform(extracted_ids)
# # extracted_ids_format = extracted_ids_format["id"].to_list()
# extracted_ids_original = extracted_ids["id"].to_list()
# print(extracted_ids_original)
# extract_ids_full = extracted_ids_format + extracted_ids_original
# print(extract_ids_full)

# Step 2: Extract newspaper data from Qdrant collection
# newspaper_embedded_extractor = QdrantExtractorWithPayloadFilter(
#     # qdrant_url="localhost:6333",
#     qdrant_url="http://localhost:6333", #when run in docker composer
#     collection_name="backup_newspaper_embeddded",
#     payload_filter={},
#     with_vectors=["bm25_sparse", "gemini_dense_vector"],
# )

# df_ = newspaper_embedded_extractor.extract()
# print(df_.columns)

# # Step 3: Create loader
# newspaper_loader = QdrantLoader(
#     qdrant_url="http://localhost:6333", #when run in docker composer
#     destination_collection_name="newspaper_backfill",
# )

# newspaper_embedded_loader = QdrantLoader(
#     qdrant_url="http://localhost:6333", #when run in docker composer
#     destination_collection_name="backup_newspaper_embeddded",
# )

# use_case = TopicTaggingUseCase(
#     newspaper_extractor=newspaper_extractor,
#     newspaper_embedded_extractor=newspaper_embedded_extractor,
#     newspaper_loader=newspaper_loader,
#     newspaper_embedded_loader=newspaper_embedded_loader,
# )

# df_ = use_case.run()
# print(df_)