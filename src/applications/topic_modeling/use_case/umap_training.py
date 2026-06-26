from src.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
import numpy as np
from src.applications.topic_modeling.training.training_umap import TrainingUmap
import polars as pl



class TrainingUMAPUseCase:
    def extract(self) -> None:
        """
            Extract all data from Qdrant.
        """
        extractor = QdrantExtractorWithPayloadFilter(
            # qdrant_url="http://localhost:6333",
            qdrant_url="http://qdrant:6333", #when run in docker composer
            collection_name="newspaper_embedded",
            payload_filter={},
            with_vectors=True,
        )
        df_ = extractor.extract()
        return df_

    def transform(self, df: pl.DataFrame) -> np.ndarray:
        """
            Transform the data.
            Convert polars dataframe to numpy array.
        """
        vectors = df.get_column("vector")
        x_train = np.vstack(vectors.to_numpy())
        return x_train

    def train(self) -> None:
        """
            Train the UMAP model.
        """
        df_ = self.extract()
        print(f"Done query data from Qdrant, with number of training samples: {len(df_)}")
        x_train = self.transform(df_)
        print(f"Done transform data, with shape: {x_train.shape}")
        training_umap = TrainingUmap()
        training_umap.train(x_train)
        print("Done train UMAP model")





    
