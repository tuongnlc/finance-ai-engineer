import json
import os

from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from ai_engineer.applications.topic_tagging.application.models import TopicTaggingDAB
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister
from ai_engineer.shared.data_pipeline.extract.dela_extractor import DeltaExtractor
from ai_engineer.shared.data_pipeline.transform.spark.columns import SelectColumns
from ai_engineer.shared.data_pipeline.transform.spark.join_df import JoinDataFrame
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType, StructField, StructType
from ai_engineer.shared.data_pipeline.load.delta_loader import DeltaMergeLoaderWithSpark
from databricks.sdk.runtime import dbutils


class TopicTaggingUseCaseDAB:
    """
        Do topic tagging. Then load to multiple collections. Including:
        - newspaper for topic_summary downstream task
    """
    def __init__(
            self,
            newspaper_extractor: DeltaExtractor,
            newspaper_tagging_extractor: DeltaExtractor,
            newspaper_tagging_loader: DeltaMergeLoaderWithSpark,
        ):
        self.newspaper_extractor = newspaper_extractor
        self.newspaper_tagging_extractor = newspaper_tagging_extractor
        self.newspaper_tagging_loader = newspaper_tagging_loader

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

    def extract(self, run_date: str | None = None, source_link: str | None = None):
        # Extract data from delta table. Then compare with id in newspaper_tagging_model
        df_newspaper = self.newspaper_extractor.extract()
        df_newspaper_tagging = self.newspaper_tagging_extractor.extract()

        # Dynamic date filter phục vụ backfill: chỉ giữ bản tin có publish_date
        # bằng ngày job chạy (job.start_time.iso_date).
        if run_date is not None:
            df_newspaper = df_newspaper.filter(
                F.to_date(F.col("publish_date")) == F.lit(run_date)
            )
        print(f"After filter by run_date: {df_newspaper.count()} rows from delta table")
               
        if source_link is not None:
            df_newspaper = df_newspaper.filter(
                F.col("source_link") == F.lit(source_link)
            )
        print(f"After filter by source_link: {df_newspaper.count()} rows from delta table")

        # Filter only row not in newspaper_tagging_model
        # left_anti: giữ các row của df_newspaper KHÔNG match newspaper_url bên phải
        df_newspaper = df_newspaper.join(
            df_newspaper_tagging.select("newspaper_url").distinct(),
            on="newspaper_url",
            how="left_anti",
        )

        print(f"Extracted {df_newspaper.count()} rows for calling llm")

        return df_newspaper

    def transform(self, df: DataFrame):
        """
            Add article column to original dataframe
            New column value is a json string of article with id, title, description, content.
            This column is send to llm to get topic tagging output.

            Example of article column value:
            {
                "title": "Title of the article",
                "content": "Content of the article"
            }

            parse article column value
            :param df: The dataframe to transform
            :return: The dataframe with the article column
        """
        article_struct = F.struct(
            F.col("newspaper_url").alias("newspaper_url"),
            F.col("newspaper_title").alias("title"),
            F.col("newspaper_content").alias("content"),
        )

        df = df.withColumn(
            "article",
            F.to_json(article_struct, {"ignoreNullFields": "false"}
            )
        )
        return df

    def call_llm(self, df: DataFrame):
        """
            Call llm to get topic tagging output

            output is a list of TopicTagging object with columns as below:
            - id: The id of the article (document_id)
            - main_topic: The main topic of the article
            - stocks_mention: The stocks mentioned in the article
            - person_mention: The person mentioned in the article
            - newspaper_summary: The summary of the article

            :param df: The dataframe to call llm
            :return: The dataframe with the topic tagging output
        """
        parser = PydanticOutputParser(pydantic_object=TopicTaggingDAB)

        topic_tagging_prompt = PromptRegister().load_and_parse_prompt("prompts:/finance_agent_2026.finance_agent_2026_prompt.topic_tagging_prompt_dab@production")
        prompt = topic_tagging_prompt.partial(format_instructions=parser.get_format_instructions())

        articles = [json.loads(row["article"]) for row in df.select("article").collect()]

        api_key = dbutils.secrets.get(scope = "databricks-access-token", key = "databricks-access-token")

        llm = ChatOpenAI(
            model="system.ai.gpt-oss-120b",
            api_key=api_key,
            base_url="https://dbc-a4257ab8-9fcb.cloud.databricks.com/ai-gateway/mlflow/v1",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=0,
        )

        chain = prompt | llm | parser
        llm_output = []

        import time
        start_time = time.time()
        MAX_CONCURRENCY = 1
        retry_chain = chain.with_retry(wait_exponential_jitter=True, stop_after_attempt=5)
        results = retry_chain.batch(articles, config={"max_concurrency": MAX_CONCURRENCY})
        end_time = time.time()
        print(f"Time to call llm: {end_time - start_time} seconds")


        for idx, result in enumerate(results, start=1):
            result = result.model_dump()

            result = { # chỉ normalize các tag field, giữ nguyên các field còn lại, (các key này để filter)
                key: self._lowercase_text(value) if key in ("main_topic", "stocks_mention") else value
                for key, value in result.items()
            }

            print(f"=== Result {idx} ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            llm_output.append(result)

        schema = StructType(
            [
                StructField("newspaper_url", StringType(), False),
                StructField("main_topic", ArrayType(StringType()), True),
                StructField("stocks_mention", ArrayType(StringType()), True),
                StructField("person_mention", ArrayType(StringType()), True),
                StructField("newspaper_summary", StringType(), True),
                StructField("sentiment_analysis", StringType(), True),
            ]
        )

        df_llm_output = df.sparkSession.createDataFrame(llm_output, schema=schema)
        return df_llm_output

    def load_data_to_newspaper_collection(self, df_llm_output: DataFrame, newspaper_df: DataFrame):
        """
            Join topic tagging output (llm_output) to newspaper data
            Casue two dataframe have same newspaper_url column(document_url), so condition to join is

            + type: left_join
            + left_on: newspaper_url (from newspaper_df)
            + right_on: newspaper_url (from df_llm_output)
        """
        new_cols = [
            "stocks_mention",
            "main_topic",
            "person_mention",
            "newspaper_summary",
            "sentiment_analysis",
        ]

        base_cols = [
            "newspaper_title",
            "newspaper_url",
            "publish_date",
            "newspaper_content"
        ]

        try:
            joined_data = JoinDataFrame(
                    left_on="newspaper_url",
                    right_on="newspaper_url",
                    how="left",
                ).transform(
                    df_left=newspaper_df,
                    df_right=df_llm_output.select(["newspaper_url", *new_cols]),
                )
            newspaper_data_final = SelectColumns([*base_cols, *new_cols]).transform(joined_data)

        except Exception as e:
            print(f"Enrichment join failed, fallback to base columns only: {e}")
            raise e
        print("Enrichment join success. Start loading data to delta table")
        self.newspaper_tagging_loader.load(newspaper_data_final)

        return newspaper_data_final

    def run(self, run_date: str | None = None, source_link: str | None = None):
        df_newspaper = self.extract(run_date, source_link)
        df_newspaper = self.transform(df_newspaper)

        if df_newspaper.count() ==0:
            return None
        else:
            df_llm_output = self.call_llm(df_newspaper)
            newspaper_data_final = self.load_data_to_newspaper_collection(df_llm_output, df_newspaper)
            print(newspaper_data_final)
            return newspaper_data_final
