import json

import pandas as pd
from sqlalchemy import create_engine

from my_project.config import AppConfig
from my_project.orchestration.tasks import run_orders_pipeline


def test_run_orders_pipeline(tmp_path):
    source_path = tmp_path / "orders.json"
    source_path.write_text(
        json.dumps(
            {
                "orders": [
                    {"order_id": 1, "customer_id": 10, "amount": "10.5", "status": " NEW "},
                    {"order_id": 2, "customer_id": 20, "amount": 12, "status": "shipped"},
                    {"order_id": 2, "customer_id": 20, "amount": 12, "status": "SHIPPED"},
                ]
            }
        ),
        encoding="utf-8",
    )

    db_path = tmp_path / "warehouse.db"
    artifact_path = tmp_path / "orders.parquet"
    lineage_path = tmp_path / "lineage.jsonl"

    config = AppConfig.model_validate(
        {
            "app": {"name": "test-project", "env": "test", "log_level": "DEBUG"},
            "pipeline": {"batch_size": 100},
            "source": {
                "url": str(source_path),
                "timeout_seconds": 5,
                "retries": 1,
                "backoff_seconds": 0.1,
                "verify_ssl": True,
            },
            "warehouse": {
                "db_url": f"sqlite:///{db_path}",
                "table_name": "orders",
                "if_exists": "replace",
                "artifact_path": artifact_path,
            },
            "observability": {"lineage_path": lineage_path},
        }
    )

    result = run_orders_pipeline(config)

    assert result.extracted_rows == 3
    assert result.transformed_rows == 2
    assert result.loaded_rows == 2
    assert artifact_path.exists()
    assert lineage_path.exists()

    engine = create_engine(f"sqlite:///{db_path}", future=True)
    loaded = pd.read_sql_query("select * from orders order by order_id", engine)
    engine.dispose()

    assert loaded["order_id"].tolist() == [1, 2]
    assert loaded["status"].tolist() == ["new", "shipped"]
