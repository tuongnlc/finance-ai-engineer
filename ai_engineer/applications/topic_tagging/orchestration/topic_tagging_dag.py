from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from ai_engineer.applications.topic_tagging.orchestration.python_script.topic_tagging import main


with DAG(
    dag_id='2027_07_07_topic_tagging',
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    tags=['Topic Tagging'],   
) as dag:
    # Task 1: Bash execution
    start_topic_tagging_dag = BashOperator(
        task_id='start_topic_tagging_dag',
        bash_command='echo "Start Topic Tagging!"'
    )

    # Task 2: Python execution
    topic_tagging = PythonOperator(
        task_id='topic_tagging_task',
        python_callable=main,
    )

    start_topic_tagging_dag >> topic_tagging  
