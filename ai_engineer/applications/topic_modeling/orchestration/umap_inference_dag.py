from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from ai_engineer.applications.topic_modeling.orchestration.python_script.umap_inference import main


last_publish_date = "{{ ds }}"


with DAG(
    dag_id='2026_23_06_inference_umap',
    start_date=datetime(2026, 6, 23),
    schedule='@daily',
    catchup=True,
    tags=['UMAP', 'Inference'],   
) as dag:
    # Task 1: Bash execution
    start_training_umap_dag = BashOperator(
        task_id='start_training_umap_dag',
        bash_command='echo "Start Training UMAP Model!"'
    )

    # Task 2: Python execution
    training_umap = PythonOperator(
        task_id='training_umap_task',
        python_callable=main,
        op_kwargs={'publish_date': last_publish_date}
    )

    start_training_umap_dag >> training_umap  
