from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader


loader = QdrantLoader(
    qdrant_url="http://qdrant:6333",
    destination_collection_name="newspaper_summary",
)

def main(publish_date: str):
    loader.delete_before_load(publish_date)