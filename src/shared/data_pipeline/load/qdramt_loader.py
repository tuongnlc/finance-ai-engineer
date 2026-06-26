"""
    Receive data from postgresql database and load to qdrant database
"""
from qdrant_client import QdrantClient
from pydantic import BaseModel
import polars as pl
from qdrant_client.models import PointStruct
from src.shared.data_pipeline.load.base import BaseLoader


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
            ) -> None:
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.destination_collection_name = destination_collection_name
    
    def _payload_to_dict(self, payload: BaseModel | dict) -> dict:
        if isinstance(payload, dict):
            return payload
        if hasattr(payload, "model_dump"):
            return payload.model_dump(mode="json")
        return dict(payload)

    def load(self, records: pl.DataFrame, vector_column: str | None):
        """
            Load arrow table to qdrant database
        """
        if records.height == 0:
            return

        print("NUMBER of vector to write to qdrant:")
        print(len(records))

        points = []
        for item in records.to_dicts():
            payload_dict = {
                    key: value
                    for key, value in item.items()
                    if key != "id" and key != vector_column
                }


            if vector_column is None:
                points.append(
                    PointStruct(
                        id=item["id"],
                        vector={},
                        payload=payload_dict,
                    )
                )
            else:
                points.append(
                    PointStruct(
                        id=item["id"],
                        vector=item[vector_column],
                        payload=payload_dict,
                    )
                )
            print(points[-1])

        self.qdrant_client.upload_points(
            collection_name=self.destination_collection_name,
            points=points,
            wait=False, # Set False để tăng tốc độ nếu không cần đọc ngay lập tức
            batch_size=10,
        )
