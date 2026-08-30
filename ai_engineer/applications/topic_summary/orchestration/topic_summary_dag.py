import os
import random
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from ai_engineer.applications.topic_summary.orchestration.python_script.topic_summary import (
    main as topic_summary_main,
    GCP_API_KEY_NAMES,
)


def _pick_three_distinct_keys():
    key_name_1, key_name_2, key_name_3 = random.sample(GCP_API_KEY_NAMES, 3)
    return os.getenv(key_name_1), os.getenv(key_name_2), os.getenv(key_name_3)


_llm_key_business, _llm_key_macro, _llm_key_market = _pick_three_distinct_keys()


_PUBLISH_DATE_TEMPLATE = (
    "{% if params.export_date %}"
    "{{ params.export_date }}"
    "{% else %}"
    "{{ ds }}"
    "{% endif %}"
)


with DAG(
    dag_id='2026_08_29_topic_summary',
    start_date=datetime(2026, 8, 21),
    schedule=None,
    catchup=False,
    tags=['Topic Summary'],
    render_template_as_native_obj=True,
    params={
        'export_date': None,
    },
) as dag:
    start_topic_dag = BashOperator(
        task_id='start_topic_summary_dag',
        bash_command='echo "Start Topic Summary!"'
    )

    topic_summary__business = PythonOperator(
        task_id='topic_summary__business',
        python_callable=topic_summary_main,
        op_kwargs={
            'publish_date': _PUBLISH_DATE_TEMPLATE,
            'topic_type': 'business',
            'llm_api_key': _llm_key_business,
        },
    )

    topic_summary__macro = PythonOperator(
        task_id='topic_summary__macro',
        python_callable=topic_summary_main,
        op_kwargs={
            'publish_date': _PUBLISH_DATE_TEMPLATE,
            'topic_type': 'macro',
            'llm_api_key': _llm_key_macro,
        },
    )

    topic_summary__market = PythonOperator(
        task_id='topic_summary__market',
        python_callable=topic_summary_main,
        op_kwargs={
            'publish_date': _PUBLISH_DATE_TEMPLATE,
            'topic_type': 'market',
            'llm_api_key': _llm_key_market,
        },
    )

    start_topic_dag >> [topic_summary__business, topic_summary__macro, topic_summary__market]