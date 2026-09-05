import random
from unidecode import unidecode
from ai_engineer.shared.data_pipeline.load.qdrant_loader import QdrantLoader
from ai_engineer.applications.topic_tagging.application.prompt.prompt_loading import TopicTaggingPromptLoading
from ai_engineer.applications.topic_tagging.application.models import TopicTagging
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
import polars as pl
import json
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
from dotenv import load_dotenv
from ai_engineer.shared.data_pipeline.transform.columns import DropColumns, ReplaceCharInColumn, SelectColumns, AddColumn
from ai_engineer.shared.data_pipeline.transform.join_df import JoinDataFrame
from ai_engineer.shared.data_pipeline.transform.parse_sparse_vector import ParseSparseVector
# DropColumns

load_dotenv()

list_of_api_keys = [
    "GCP_PROJECT_1",
    "GCP_PROJECT_2",
    "GCP_PROJECT_3",
    "GCP_PROJECT_4",
    "GCP_PROJECT_5",
    "GCP_PROJECT_6",
    "GCP_PROJECT_7",
    "GCP_PROJECT_8",
]

api_key = random.choice(list_of_api_keys)

topic_tagging_api_key = os.getenv(api_key)
topic_tagging_model = os.getenv("TOPIC_TAGGING_MODEL")
BATCH_SIZE = 15
BATCH_SLEEP_SECONDS = 60

class TopicTaggingUseCase:
    """
        Do topic tagging. Then load to multiple collections. Including:
        - newspaper for topic_summary downstream task
        - newspaper_embedded for rag filter downstream task
    """
    def __init__(
            self,
            newspaper_extractor: QdrantExtractorWithPayloadFilter,
            newspaper_embedded_extractor: QdrantExtractorWithPayloadFilter,
            newspaper_loader: QdrantLoader,
            newspaper_embedded_loader: QdrantLoader
        ):
        self.newspaper_extractor = newspaper_extractor
        self.newspaper_embedded_extractor = newspaper_embedded_extractor
        self.newspaper_loader = newspaper_loader
        self.newspaper_embedded_loader = newspaper_embedded_loader

    @staticmethod
    def _build_article(x: dict):
        return json.dumps(
            {
                "id": x["id"],
                "title": x["newspaper_title"],
                "description": x["newspaper_summary"],
                "content": x["newspaper_content"],
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _lowercase_text(value=None):
        if value is None:
            return None
        if isinstance(value, str):
            return value.lower()
        if isinstance(value, list):
            return [
                item.lower() if isinstance(item, str) else item
                for item in value
            ]
        return value

    def extract_newspaper(self):
        df_newspaper = self.newspaper_extractor.extract()
        extracted_ids = df_newspaper.select(["id"])
        extracted_ids_original = extracted_ids["id"].to_list()

        extracted_ids_format = ReplaceCharInColumn("id", "-", "").transform(extracted_ids)
        extracted_ids_format = extracted_ids_format["id"].to_list()
        extract_ids_full = extracted_ids_format + extracted_ids_original #get ids(document_id) to use as filter for extract newspaper_embedded collection
        return df_newspaper, extract_ids_full    

    def extract_newspaper_embedded(self, document_ids: list | None = None):
        override_filter = {"document_id": document_ids}
        df_newspaper_embedded = self.newspaper_embedded_extractor.extract(override_payload_filter=override_filter)
        return df_newspaper_embedded

    def transform(self, df: pl.DataFrame):
        """
            Add article column to original dataframe
            New column value is a json string of article with id, title, description, content.
            This column is send to llm to get topic tagging output.

            Example of article column value:
            {
                "id": "123",
                "title": "Title of the article",
                "description": "Summary of the article",
                "content": "Content of the article"
            }

            parse article column value
            :param df: The dataframe to transform
            :return: The dataframe with the article column
        """
        df = df.with_columns(
            pl.struct(["id", "newspaper_title", "newspaper_summary", "newspaper_content"])
            .map_elements(self._build_article, return_dtype=pl.Utf8)
            .alias("article")
        )
        return df

    def call_llm(self, df: pl.DataFrame):
        """
            Call llm to get topic tagging output

            output is a list of TopicTagging object with columns as below:
            - id: The id of the article (document_id)
            - main_topic: The main topic of the article
            - stocks_mention: The stocks mentioned in the article
            - person_mention: The person mentioned in the article

            :param df: The dataframe to call llm
            :return: The dataframe with the topic tagging output
        """
        #prepare parser
        parser = PydanticOutputParser(pydantic_object=TopicTagging)

        # prepare prompt
        topic_tagging_prompt = TopicTaggingPromptLoading().load_and_parse_prompt()
        prompt = topic_tagging_prompt.partial(format_instructions=parser.get_format_instructions())

        #prepare data
        articles = [json.loads(article) for article in df.get_column("article").to_list()]

        #prepare llm
        llm = ChatGoogleGenerativeAI(
            model=topic_tagging_model,
            api_key=topic_tagging_api_key,
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=0,
        )

        chain = prompt | llm | parser
        llm_output = []
        for batch_start in range(0, len(articles), BATCH_SIZE):
            batch_number = (batch_start // BATCH_SIZE) + 1
            batch_articles = articles[batch_start: batch_start + BATCH_SIZE]

            start_time_batch = time.time()
            results = chain.batch(batch_articles, config={"max_concurrency": BATCH_SIZE})
            end_time_batch = time.time()

            for idx, result in enumerate(results, start=batch_start + 1):
                result = result.model_dump()
                
                result = { #normalize all value except id
                    key: value if key == "id" else self._lowercase_text(value)
                    for key, value in result.items()
                }
                
                print(f"=== Result {idx} ===")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                llm_output.append(result)

            if batch_start + BATCH_SIZE < len(articles):
                print(f"Batch {batch_number} completed in {end_time_batch - start_time_batch}s")
                print(
                    f"Batch {batch_number} completed. Sleeping {BATCH_SLEEP_SECONDS}s before next batch..."
                )
                time.sleep(BATCH_SLEEP_SECONDS)

        df_llm_output = pl.DataFrame(llm_output)
        return df_llm_output

    def load_data_to_newspaper_collection(self, df_llm_output: pl.DataFrame, newspaper_df: pl.DataFrame):
        """
            Join topic tagging output (llm_output) to newspaper data
            Casue two dataframe have same id column(document_id), so condition to join is

            + type: left_join
            + left_on: id (from newspaper_df)
            + right_on: id (from df_llm_output)
        """
        new_cols = [
            "stocks_mention",
            "main_topic",
            "person_mention",
        ]

        #drop all column if columns exist in original df
        newspaper_data_join = DropColumns(new_cols).transform(newspaper_df)

        base_cols = [
            "id",
            "newspaper_title",
            "newspaper_url",
            "publish_date",
            "newspaper_content",
            "newspaper_summary",
            "is_embedded",
            "created_at",
        ]
        newspaper_data_final = SelectColumns(base_cols).transform(newspaper_data_join)

        try:
            joined_data = JoinDataFrame(
                    left_on="id",
                    right_on="id",
                    how="left",
                ).transform(
                    df_left=newspaper_data_final,
                    df_right=df_llm_output.select(["id", *new_cols]),
                )
            newspaper_data_final = SelectColumns([*base_cols, *new_cols]).transform(joined_data)

            # Need to keep is_topic_tagging as 0 before loading data to newspaper_embedded collection finished
            newspaper_data_final = AddColumn("is_topic_tagging", 0).transform(newspaper_data_final)
            self.newspaper_loader.load(newspaper_data_final)
        except Exception as e:
            print(f"Enrichment join failed, fallback to base columns only: {e}")
        self.newspaper_loader.load(newspaper_data_final)  

    def load_data_to_newspaper_embedded_collection(self, 
            df_llm_output: pl.DataFrame, 
            newspaper_embedded_df: pl.DataFrame,
            dense_vector_column: str,
            sparse_vector_indices_column: str,
            sparse_vector_values_column: str,
        ):
        """
            Join topic tagging output (llm_output) to newspaper data
            Cause newspaper_embedded_df have document_id column, so condition to join is

            + type: inner_join
            + left_on: document_id (from newspaper_embedded_df)
            + right_on: id (from df_llm_output)
        """
        new_cols = [
            "stocks_mention",
            "main_topic",
            "person_mention",
        ]

        #drop all column if columns exist in original df
        if any(c in newspaper_embedded_df.columns for c in new_cols):
            newspaper_embedded_data_join = DropColumns(new_cols).transform(newspaper_embedded_df)
        else:
            newspaper_embedded_data_join = newspaper_embedded_df
        print("Testing here")
        print(newspaper_embedded_data_join)

        base_cols = [
            "id",
            "document_id",
            "publish_date",
            "chunk_content",
            "chunk_index",
            "bm25_sparse",
            "gemini_dense_vector",
        ]

        newspaper_embedded_data_final = SelectColumns(base_cols).transform(newspaper_embedded_data_join) 
        newspaper_embedded_data_final = ParseSparseVector("bm25_sparse", "bm25_sparse_indices", "bm25_sparse_values").transform(newspaper_embedded_data_final)

        base_cols_after_sparse_parse = [c for c in base_cols if c != "bm25_sparse"] + ["bm25_sparse_indices", "bm25_sparse_values"]

        try:
            # joined = newspaper_embedded_data_final.join(df_llm_output.select(["id", *new_cols]), on="id", how="left")
            df_llm_output = df_llm_output.select(["id", *new_cols])
            joined = JoinDataFrame(
                    left_on="document_id",
                    right_on="id",
                    how="inner",
                ).transform(
                    df_left=newspaper_embedded_data_final,
                    df_right=df_llm_output,
                )
            newspaper_embedded_data_final = SelectColumns([*base_cols_after_sparse_parse, *new_cols]).transform(joined)

            print("Data for newspaper embedded collection:")
            print(newspaper_embedded_data_final)
            print(newspaper_embedded_data_final.columns)
        except Exception as e:
            raise e
        
        self.newspaper_embedded_loader.load(newspaper_embedded_data_final, 
            dense_vector_column=dense_vector_column,
            sparse_vector_indices_column=sparse_vector_indices_column,
            sparse_vector_values_column=sparse_vector_values_column,
        )  

    def _update_is_topic_tagging_to_one(self, df: pl.DataFrame):
        df = AddColumn("is_topic_tagging", 1).transform(df)

        self.newspaper_loader.load(df)
        return df

    def _close_clients(self):
        for component in (self.newspaper_extractor, self.newspaper_loader):
            client = getattr(component, "qdrant_client", None)
            if client is not None:
                client.close()

    def run(self):
        try:
            df_newspaper, extract_ids_full = self.extract_newspaper()
            df_newspaper_embedded = self.extract_newspaper_embedded(document_ids=extract_ids_full)
            # print()

            df_newspaper = self.transform(df_newspaper)
            
            start_time = time.time()
            llm_output = self.call_llm(df_newspaper)
            end_time = time.time()
            print(f"LLM inference time: {end_time - start_time}")

            self.load_data_to_newspaper_collection(llm_output, df_newspaper)
            self.load_data_to_newspaper_embedded_collection(
                llm_output,
                df_newspaper_embedded,
                dense_vector_column="gemini_dense_vector",
                sparse_vector_indices_column="bm25_sparse_indices",
                sparse_vector_values_column="bm25_sparse_values",
            )
            self._update_is_topic_tagging_to_one(df_newspaper)

        finally:
            self._close_clients()
        
