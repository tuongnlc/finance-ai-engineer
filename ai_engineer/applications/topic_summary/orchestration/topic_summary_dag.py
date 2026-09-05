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


def _pick_five_distinct_keys():
    key_name_1, key_name_2, key_name_3, key_name_4, key_name_5 = random.sample(GCP_API_KEY_NAMES, 5)
    return os.getenv(key_name_1), os.getenv(key_name_2), os.getenv(key_name_3), os.getenv(key_name_4), os.getenv(key_name_5)


_llm_key_business, _llm_key_macro, _llm_key_market, _llm_key_fund, _llm_key_law = _pick_five_distinct_keys()


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

    topic_summary__fund = PythonOperator(
        task_id='topic_summary__fund',
        python_callable=topic_summary_main,
        op_kwargs={
            'publish_date': _PUBLISH_DATE_TEMPLATE,
            'topic_type': 'fund',
            'llm_api_key': _llm_key_fund,
        },
    )

    topic_summary__law = PythonOperator(
        task_id='topic_summary__law',
        python_callable=topic_summary_main,
        op_kwargs={
            'publish_date': _PUBLISH_DATE_TEMPLATE,
            'topic_type': 'law',
            'llm_api_key': _llm_key_law,
        },
    )

    start_topic_dag >> topic_summary__business >> topic_summary__macro >> topic_summary__market >> topic_summary__fund >> topic_summary__law
