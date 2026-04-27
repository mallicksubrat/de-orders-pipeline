import json

from my_project.config import SourceSettings
from my_project.extractors.orders_api import fetch_orders


def test_fetch_orders_from_local_json(tmp_path):
    source_path = tmp_path / "orders.json"
    source_path.write_text(
        json.dumps(
            {
                "orders": [
                    {"order_id": 1, "customer_id": 10, "amount": "10.5", "status": "new"}
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = fetch_orders(
        SourceSettings(
            url=str(source_path),
            timeout_seconds=5,
            retries=0,
            backoff_seconds=0.0,
            verify_ssl=True,
        )
    )

    assert rows == [{"order_id": 1, "customer_id": 10, "amount": "10.5", "status": "new"}]
