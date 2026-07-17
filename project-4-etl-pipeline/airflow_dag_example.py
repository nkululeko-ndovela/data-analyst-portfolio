"""
Illustrative only — shows how pipeline.py's extract/quality_checks/transform/load
functions would be wired into an Airflow DAG for daily orchestration in production.
Not meant to be run standalone (requires an Airflow environment); included to
demonstrate orchestration design, since the pipeline itself is runnable directly.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import pipeline

default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
    "email_on_failure": True,
}

with DAG(
    dag_id="daily_orders_etl",
    description="Extract daily orders batch, run quality gate, transform, load to warehouse",
    default_args=default_args,
    schedule_interval="0 3 * * *",  # 3 AM daily, after upstream batch file lands
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["etl", "orders", "warehouse"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=lambda: pipeline.extract(pipeline.SOURCE_PATH),
    )

    quality_gate_task = PythonOperator(
        task_id="quality_gate",
        python_callable=pipeline.quality_checks,
        op_args=[extract_task.output],
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=pipeline.transform,
        op_args=[extract_task.output],
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=pipeline.load,
        op_args=[transform_task.output],
    )

    extract_task >> quality_gate_task >> transform_task >> load_task
