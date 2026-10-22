from dotenv import load_dotenv
import os

from ai_engineer.shared.data_pipeline.load.postrgesql_loader import PostgreDBLoaderWithPolars

load_dotenv()

POSTGRES_URI = (
    f"postgresql://{os.getenv('POSTGRES_USER_CHATBOT', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD_CHATBOT', 'postgres')}@"
    f"{os.getenv('POSTGRES_HOST_CHATBOT', 'chatbot_postgres')}:"
    f"{os.getenv('POSTGRES_PORT_CHATBOT', '5432')}/"
    f"{os.getenv('POSTGRES_DB_CHATBOT', 'chatbot_db')}"
)

loader = PostgreDBLoaderWithPolars(
    destination_table_name="newspaper_summary",
    uri=POSTGRES_URI,
    delete_filter_column="publish_date",
    delete_filter_type="date",
)

def main(publish_date: str):
    loader.delete_before_load(publish_date)
