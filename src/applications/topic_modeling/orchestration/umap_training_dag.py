from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
# from orchestration.python_script.crawl_market_data_v1 import main
from src.applications.topic_modeling.orchestration.python_script.umap_training import main



with DAG(
    dag_id='2026_23_06_training_umap',
    start_date=datetime(2026, 6, 21),
    schedule='@weekly',
    catchup=False,
    tags=['UMAP', 'Training'],   
) as dag:
    # Task 1: Bash execution
    start_training_umap_dag = BashOperator(
        task_id='start_training_umap_dag',
        bash_command='echo "Start Training UMAP Model!"'
    )

    # Task 2: Python execution
    inference_umap_task = PythonOperator(
        task_id='inference_umap_task',
        python_callable=main,
    )

    start_training_umap_dag >> inference_umap_task  
