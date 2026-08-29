from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from ai_engineer.applications.topic_summary.orchestration.python_script.topic_summary import main as topic_summary_task

# logical_data = {"ds"}

with DAG(
    dag_id='2026_08_29_topic_summary',
    start_date=datetime(2026, 8, 21),
    schedule=None,
    catchup=False,
    tags=['Topic Summary'],   
) as dag:
    # Task 1: Bash execution
    start_topic_dag = BashOperator(
        task_id='start_topic_summary_dag',
        bash_command='echo "Start Topic Summary!"'  
    )

    # Task 2: Python execution
    topic_summary = PythonOperator(
        task_id='topic_summary_task',
        python_callable=topic_summary_task,
    )

    start_topic_dag >> topic_summary