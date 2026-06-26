# Step 1: Load data

# Step 2: Do transform

# Step 3: Do train and upload to MLFlow
from src.shared.data_pipeline.transform.columns import SelectColumns
from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
import numpy as np
# from src.applications.topic_modeling.training.training_umap import TrainingUmap
from src.applications.topic_modeling.inference.inference_umap import InferenceUmap
import polars as pl
from src.shared.data_pipeline.load.qdramt_loader import QdrantLoader
from datetime import date

class InferenceUMAPUseCase:
    def __init__(
        self,
            publish_date: date 
        ) -> None:
            self.publish_date = publish_date
        
    def extract(self) -> None:
        """
            Extract all data from Qdrant.
        """
        extractor = QdrantExtractorWithPayloadFilter(
            # qdrant_url="http://localhost:6333",
            qdrant_url="http://qdrant:6333", #when run in docker composer
            collection_name="newspaper_embedded",
            payload_filter={
                "publish_date": f"{self.publish_date}", # receive from airflow
            },
            with_vectors=True,
        )
        df_ = extractor.extract()
        return df_


    def predict(self) -> None:
        """
            Predict with the UMAP model.
        """
        df_ = self.extract() #return df
        print(f"Done query data from Qdrant, with number of training samples: {len(df_)}")
      
        umap = InferenceUmap()
        df_output = umap.predict(df_)
        print(f"Done predict data, with shape: {df_output.shape}")

        return df_output

    def transform(self, df_: pl.DataFrame) -> None:
        """
            Choose suitable column to repair data before load to Qdrant.
        """
        transform_step = SelectColumns(columns=["id", "document_id", "publish_date", "vector_umap", "chunk_content", "chunk_index"])
        df_with_umap = transform_step.transform(df_)
        print(f"Done transform data, with shape: {df_with_umap.shape}")
        return df_with_umap

    def load(self, 
                destination_collection_name: str = "newspaper_topic_modelling_embedded",
                # qdrant_url: str = "http://localhost:6333",
                qdrant_url: str = "http://qdrant:6333", #when run in docker composer
            ) -> None:
        """
            Load the UMAP model.
        """
        prediction_data = self.predict()
        df_with_umap = self.transform(prediction_data)
        print(f"Done transform data, with number of training samples: {len(df_with_umap)}")
        loader = QdrantLoader(
            qdrant_url=qdrant_url,
            destination_collection_name=destination_collection_name,
        )
        loader.load(df_with_umap, vector_column="vector_umap")
        print("Load to qdrant database done")
    
