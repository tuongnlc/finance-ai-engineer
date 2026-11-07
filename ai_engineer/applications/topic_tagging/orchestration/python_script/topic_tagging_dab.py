import sys

from ai_engineer.applications.topic_tagging.use_case.topic_tagging_dab import TopicTaggingUseCaseDAB
from ai_engineer.shared.data_pipeline.extract.dela_extractor import DeltaExtractor
from ai_engineer.shared.data_pipeline.load.delta_loader import DeltaMergeLoaderWithSpark
from pyspark.sql import SparkSession


TAGGING_TABLE = "market_news_datamart.newspaper.newspaper_topic_tagging"


def main():
    # Cac tham so duoc truyen tu Databricks job parameters (python_wheel_task.parameters):
    #   argv[1] = run_date    ({{job.start_time.iso_date}}) - mac dinh la ngay job chay, dung cho backfill.
    #   argv[2] = source_link ({{job.parameters.source_link}})
    #   argv[3] = merge_keys (danh sach cot khoa, phan tach bang dau phay)
    #   argv[4] = partition_column (cot partition cua bang target)
    run_date = sys.argv[1] if len(sys.argv) > 1 else None
    source_link = sys.argv[2] if len(sys.argv) > 2 else None
    merge_keys_raw = sys.argv[3] if len(sys.argv) > 3 else None
    partition_column = sys.argv[4] if len(sys.argv) > 4 else None

    merge_keys = (
        [key.strip() for key in merge_keys_raw.split(",") if key.strip()]
        if merge_keys_raw
        else ["newspaper_url"]
    )

    spark = SparkSession.builder.getOrCreate()

    newspaper_extractor = DeltaExtractor(
        table_uri="market_news_datalake.newspaper.newspaper",
        spark=spark,
    )

    newspaper_tagging_extractor = DeltaExtractor(
        table_uri="market_news_datamart.newspaper.newspaper_topic_tagging",
        spark=spark,
    )

    newspaper_tagging_loader = DeltaMergeLoaderWithSpark(
        delta_table_name="market_news_datamart.newspaper.newspaper_topic_tagging",
        spark=spark,
        merge_keys=merge_keys,
        partition_column=partition_column,
    )

    use_case = TopicTaggingUseCaseDAB(
        newspaper_extractor=newspaper_extractor,
        newspaper_tagging_extractor=newspaper_tagging_extractor,
        newspaper_tagging_loader=newspaper_tagging_loader,
    )
    use_case.run(run_date=run_date, source_link=source_link)


if __name__ == "__main__":
    main()
