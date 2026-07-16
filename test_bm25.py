import re
import polars as pl
from qdrant_client import QdrantClient
from underthesea import word_tokenize
from fastembed import SparseTextEmbedding

from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader


def _tokenize_vi(text: str | None) -> str | None:
    if text is None:
        return None
    return word_tokenize(text, format="text")


def _normalize_polars_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return [
            item if isinstance(item, (str, int, float, bool)) else str(item)
            for item in value
        ]
    return str(value)


def _flatten_qdrant_vectors(vector):
    if not vector:
        return {}

    if isinstance(vector, dict):
        flattened = {}
        for vector_name, vector_value in vector.items():
            column_name = "vector" if vector_name == "" else f"vector_{vector_name}"
            if hasattr(vector_value, "indices") and hasattr(vector_value, "values"):
                flattened[f"{column_name}_indices"] = list(vector_value.indices)
                flattened[f"{column_name}_values"] = list(vector_value.values)
            else:
                flattened[column_name] = _normalize_polars_value(vector_value)
        return flattened

    return {"vector": _normalize_polars_value(vector)}


# 1. Prepare your corpus
corpus = """
Động thái chính sách này được đưa ra trong bối cảnh thanh khoản của hệ thống ngân hàng đang trải qua giai đoạn khá căng thẳng.
Điểm nhấn đáng chú ý nhất của Thông tư 25/2026 là việc nới tỷ lệ vốn ngắn hạn cho vay trung và dài hạn tối đa lên mức 40%.
Cụ thể, việc điều chỉnh các tỷ lệ an toàn sẽ trực tiếp hỗ trợ các nhà băng giảm bớt chi phí khi mở rộng bảng cân đối kế toán.
Áp lực huy động vốn dài hạn hạ nhiệt sẽ tạo ra dư địa để các ngân hàng tiến hành giảm lãi suất huy động , đặc biệt là tại các kỳ hạn dài.
Từ đó, các tổ chức tín dụng sẽ có thêm động lực để hạ lãi suất cho vay trung và dài hạn trong thời gian tới.
"""
print(len(corpus))

# 2. Tokenize the corpus for Vietnamese

tokens = word_tokenize(corpus, format="text")
# print(tokens)

bm25_model = SparseTextEmbedding(model_name="Qdrant/bm25",  disable_stemmer=True)

sparse_vec = next(bm25_model.embed([tokens]))

# # print("indices:", sparse_vec.indices)
# # print("values:", sparse_vec.values)

#extract dataframe
qdrant_extractor = QdrantExtractorWithPayloadFilter(
    qdrant_url="http://localhost:6333",
    # collection_name="bm25",
    collection_name="test_collection",
    payload_filter={"publish_date": "2026-06-24"},
    with_vectors=False,
)

# df = qdrant_extractor.extract()


qdrant_client = QdrantClient(url="http://localhost:6333", timeout=600)

records, next_offset = qdrant_client.scroll(
                collection_name="test_collection",
                # scroll_filter=Filter(
                #     FieldCondition(
                #         field="publish_date",
                #         match_type=MatchValue.MatchType.EQUAL,
                #     MatchValue("2026-06-24"),
                #     ),
                # ),
                with_payload=True,
                limit=256,
                with_vectors=True,
            )

rows = []
rows.extend(
                {
                    "id": record.id,
                    **{
                        key: _normalize_polars_value(value)
                        for key, value in (record.payload or {}).items()
                    },
                    **_flatten_qdrant_vectors(record.vector),
                }
                for record in records
            )
output_df = pl.DataFrame(rows) if rows else pl.DataFrame()
print(output_df)
# df = df.select(["id", "chunk_content", "vector"])
# df = df.with_columns(
#     pl.col("chunk_content")
#     .map_elements(_tokenize_vi, return_dtype=pl.String)
#     .alias("chunk_content_tokenized")
# )

tokenized_corpus = df["chunk_content_tokenized"].to_list()
sparse_vectors = list(bm25_model.embed(tokenized_corpus))

df = df.with_columns(
    pl.Series(
        "sparse_vector_indices",
        [vec.indices.tolist() for vec in sparse_vectors],
        strict=False,
    ),
    pl.Series(
        "sparse_vector_value",
        [vec.values.tolist() for vec in sparse_vectors],
        strict=False,
    )
)

print(
    df.select(
        [
            "id",
            "chunk_content_tokenized",
            "sparse_vector_indices",
            "sparse_vector_value",
        ]
    )
)
print(df)

#
qdrant_loader = QdrantLoader(
    qdrant_url="http://localhost:6333",
    destination_collection_name="test_collection",
)
# qdrant_loader.load(
#     df,
#     vector_column="vector",
# )
qdrant_loader.load(
    df,
    dense_vector_column="vector",
    # sparse_vector_indices_column="sparse_vector_indices",
    # sparse_vector_values_column="sparse_vector_value",
)


