from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

dag = DAG(
    "weather_pipeline",
    default_args=default_args,
    description="Weather ETL + ML Pipeline",
    schedule_interval="@daily",
    catchup=False,
)

# Run Spark ETL
etl_task = BashOperator(
    task_id="weather_etl",
    bash_command="spark-submit /opt/airflow/spark_jobs/weather_etl.py",
    dag=dag,
)

# Train ML Model
train_task = BashOperator(
    task_id="train_weather_model",
    bash_command="spark-submit /opt/airflow/spark_jobs/train_model.py",
    dag=dag,
)

etl_task >> train_task
