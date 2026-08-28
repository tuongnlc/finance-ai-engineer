import polars as pl

from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.shared.data_pipeline.transform.parse_sparse_vector import ParseSparseVector
from ai_engineer.shared.data_pipeline.transform.columns import ReplaceCharInColumn, SelectColumns
from ai_engineer.shared.data_pipeline.transform.join_df import JoinDataFrame


class AddTaggingToNewspaperEmbeddedUseCase:
    def __init__(
                self, 
                newspaper_extractor: QdrantExtractorWithPayloadFilter, 
                newspaper_embedded_extractor: QdrantExtractorWithPayloadFilter,
                loader: QdrantLoader,
                **kwargs
            ):
        self.newspaper_extractor = newspaper_extractor
        self.newspaper_embedded_extractor = newspaper_embedded_extractor
        self.loader = loader

    def run(self, **kwargs):
        # Step 1: Extract and format the newspaper data
        df_newspaper = self.newspaper_extractor.extract()
        lf_newspaper = df_newspaper.lazy()
        lf_newspaper = SelectColumns(["id", "stocks_mention", "main_topic", "person_mention"]).transform(lf_newspaper)
        lf_newspaper = ReplaceCharInColumn("id", "-", "").transform(lf_newspaper)
        df_newspaper = lf_newspaper.collect()

        # Step 2: Extract and format the newspaper embedded data
        df_newspaper_embedded = self.newspaper_embedded_extractor.extract()
        lf_newspaper_embedded = df_newspaper_embedded.lazy()
        lf_newspaper_embedded = SelectColumns(
            [
                "id",
                "document_id",
                "publish_date",
                "chunk_content",
                "chunk_index",
                "bm25_sparse",
                "gemini_dense_vector",
            ]
        ).transform(lf_newspaper_embedded)
        lf_newspaper_embedded = ReplaceCharInColumn("document_id", "-", "").transform(lf_newspaper_embedded)
        lf_newspaper_embedded = ParseSparseVector("bm25_sparse", "bm25_sparse_indices", "bm25_sparse_values").transform(lf_newspaper_embedded)
        df_newspaper_embedded = lf_newspaper_embedded.collect()        

        # Step 3: Join the two dataframe
        df = JoinDataFrame(
            left_on="document_id",
            right_on="id",
            how="inner",
        ).transform(
            df_left=df_newspaper_embedded,
            df_right=df_newspaper,
        )

        # Step 4: Load dataframe to destination collection
        # self.loader.load(df, 
        #     dense_vector_column="gemini_dense_vector",
        #     sparse_vector_indices_column="bm25_sparse_indices",
        #     sparse_vector_values_column="bm25_sparse_values",
        # )

        self.loader.load(df, 
            **kwargs
        )
        return df

        #Transform bm25_sparse column

