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

load_dotenv()

topic_tagging_api_key = os.getenv("TOPIC_TAGGING_API_KEY_1")
topic_tagging_model = os.getenv("TOPIC_TAGGING_MODEL")
BATCH_SIZE = 5
BATCH_SLEEP_SECONDS = 20

class TopicTaggingUseCase:
    def __init__(
            self,
            # publish_date: date,
            extractor: QdrantExtractorWithPayloadFilter, 
            # transformer: Transformer, 
            loader: QdrantLoader
        ):
        # Initialize the components
        self.extractor = extractor
        # self.transformer = transformer
        self.loader = loader

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

    def extract(self):
        df = self.extractor.extract()
        return df

    def transform(self, df: pl.DataFrame):
        df = df.with_columns(
            pl.struct(["id", "newspaper_title", "newspaper_summary", "newspaper_content"])
            .map_elements(self._build_article, return_dtype=pl.Utf8)
            .alias("article")
        )
        return df

    def call_llm(self, df: pl.DataFrame):
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
            results = chain.batch(batch_articles, config={"max_concurrency": BATCH_SIZE})

            for idx, result in enumerate(results, start=batch_start + 1):
                print(f"=== Result {idx} ===")
                print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
                llm_output.append(result.model_dump())

            if batch_start + BATCH_SIZE < len(articles):
                print(
                    f"Batch {batch_number} completed. Sleeping {BATCH_SLEEP_SECONDS}s before next batch..."
                )
                time.sleep(BATCH_SLEEP_SECONDS)

        df_llm_output = pl.DataFrame(llm_output)
        return df_llm_output

    @staticmethod
    def _list_join_nonempty(column: str, *, separator: str = ", ") -> pl.Expr:
        col = pl.coalesce(
            [
                pl.col(column).cast(pl.List(pl.Utf8), strict=False),
                pl.lit([], dtype=pl.List(pl.Utf8)),
            ]
        )
        return pl.when(col.list.len() > 0).then(col.list.join(separator)).otherwise(None)

    def load(self, df_llm_output: pl.DataFrame, df_: pl.DataFrame):
        df_llm_output = df_llm_output.with_columns(
            pl.concat_str(
                [
                    self._list_join_nonempty("stock_mention"),
                    self._list_join_nonempty("topic_keywords"),
                    self._list_join_nonempty("mention_people"),
                    self._list_join_nonempty("mention_stock_funds"),
                    self._list_join_nonempty("foreign_securities_funds"),
                    self._list_join_nonempty("government_policies"),
                ],
                separator=", ",
                ignore_nulls=True,
            ).alias("topic_tagging")
        )

        new_cols = [
            "stock_mention",
            "topic_keywords",
            "mention_people",
            "mention_stock_funds",
            "foreign_securities_funds",
            "government_policies",
            "topic_tagging",
        ]

        #drop all column if columns exist in original df
        data_join = df_.drop([c for c in new_cols if c in df_.columns]) # can use exclude instead

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
        data_final = data_join.select([c for c in base_cols if c in data_join.columns])

        try:
            joined = data_join.join(df_llm_output.select(["id", *new_cols]), on="id", how="left")
            data_final = joined.select([c for c in [*base_cols, *new_cols] if c in joined.columns])

            # update is_topic_tagging column to 1
            data_final = data_final.with_columns(
                pl.lit(1).cast(pl.Int8).alias("is_topic_tagging")
            )
        except Exception as e:
            print(f"Enrichment join failed, fallback to base columns only: {e}")

        self.loader.load(data_final, vector_column=None)

    def _close_clients(self):
        for component in (self.extractor, self.loader):
            client = getattr(component, "qdrant_client", None)
            if client is not None:
                client.close()

    def run(self):
        try:
            df = self.extract()
            df = self.transform(df)
            
            start_time = time.time()
            llm_output = self.call_llm(df)
            end_time = time.time()
            print(f"LLM inference time: {end_time - start_time}")

            self.load(llm_output, df)
        finally:
            self._close_clients()
        
