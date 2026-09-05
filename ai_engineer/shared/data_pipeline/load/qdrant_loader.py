"""
    Receive data from postgresql database and load to qdrant database
"""
from qdrant_client import QdrantClient
from pydantic import BaseModel
import polars as pl
from qdrant_client.models import PointStruct, SparseVector

from ai_engineer.shared.data_pipeline.load.base import BaseLoader


class QdrantLoader(BaseLoader):
    """
        Load arrow table to qdrant database
        Use Qrantclient cause polars don't support qdrant now

        Input:
            pyarrow.Table
        Output:
            None
    """
    def __init__(self, 
                qdrant_url: str,
                destination_collection_name: str,
                qdrant_payload_for_source_table: dict | None = None,
                payload_filter_for_source_table: dict | None = None,
            ) -> None:
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.destination_collection_name = destination_collection_name
        self.qdrant_payload_for_source_table = qdrant_payload_for_source_table
        self.payload_filter_for_source_table = payload_filter_for_source_table

    def load(self, 
            records: pl.DataFrame, 
            dense_vector_column: str | None = None, 
            sparse_vector_indices_column: str | None = None,
            sparse_vector_values_column: str | None = None,
        ):
        """
            Load arrow table to qdrant database
        """
        if records.height == 0:
            return

        required_columns = {"id"}
        optional_vector_columns = {
            dense_vector_column,
            sparse_vector_indices_column,
            sparse_vector_values_column,
        }
        required_columns.update(
            column_name for column_name in optional_vector_columns if column_name is not None
        )

        missing_columns = sorted(required_columns.difference(records.columns))
        if missing_columns:
            raise ValueError(
                "Missing required columns for Qdrant load: "
                f"{missing_columns}. Available columns: {records.columns}"
            )

        print("NUMBER of vector to write to qdrant:")
        print(len(records))

        dense_vector_name = None
        sparse_vector_name = None
        if sparse_vector_indices_column is not None and sparse_vector_values_column is not None:
            collection_info = self.qdrant_client.get_collection(
                self.destination_collection_name
            )
            dense_vector_name = (
                list(collection_info.config.params.vectors.keys())[0]
                if isinstance(collection_info.config.params.vectors, dict)
                else ""
            )
            sparse_vector_name = list(
                collection_info.config.params.sparse_vectors.keys()
            )[0]

        points = []
        
        for item in records.to_dicts():
            payload_dict = {
                    key: value
                    for key, value in item.items()
                    if key != "id" and key != dense_vector_column and key != sparse_vector_indices_column and key != sparse_vector_values_column
                }

            if (
                dense_vector_column is None
                and sparse_vector_indices_column is None
                and sparse_vector_values_column is None
            ):
                points.append(
                    PointStruct(
                        id=item["id"],
                        vector={},
                        payload=payload_dict,
                    )
                )
            elif sparse_vector_indices_column is None and sparse_vector_values_column is None and dense_vector_column is not None: 
                points.append(
                    PointStruct(
                        id=item["id"],
                        vector=item[dense_vector_column],
                        payload=payload_dict,
                    )
                )
            elif sparse_vector_indices_column is not None and sparse_vector_values_column is not None:
                points.append(
                    PointStruct(
                        id=item["id"],
                        vector={
                            dense_vector_name: item[dense_vector_column],
                            sparse_vector_name: SparseVector(
                                indices=item[sparse_vector_indices_column],
                                values=item[sparse_vector_values_column],
                            ),
                        },
                        payload=payload_dict,
                    )
                )

        self.qdrant_client.upload_points(
            collection_name=self.destination_collection_name,
            points=points,
            wait=False, # Set False để tăng tốc độ nếu không cần đọc ngay lập tức
            batch_size=10,
        )