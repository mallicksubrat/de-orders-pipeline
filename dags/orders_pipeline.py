from datetime import datetime

from my_project.config import load_config
from my_project.orchestration.tasks import run_orders_pipeline

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:  # pragma: no cover - Airflow is optional in the local dev environment.
    DAG = None
    PythonOperator = None


def run_pipeline():
    config = load_config()
    return run_orders_pipeline(config).model_dump(mode="json")


if DAG is not None:
    with DAG(
        dag_id="orders_pipeline",
        start_date=datetime(2024, 1, 1),
        schedule="@daily",
        catchup=False,
        tags=["orders", "batch"],
    ) as dag:
        task = PythonOperator(task_id="run_orders", python_callable=run_pipeline)
else:  # pragma: no cover - used only when Airflow is not installed.
    dag = None
