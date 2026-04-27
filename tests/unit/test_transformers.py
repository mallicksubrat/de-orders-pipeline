import pytest

from my_project.exceptions import TransformationError
from my_project.transformers.clean_orders import transform


def test_transform():
    rows = [
        {"order_id": 1, "customer_id": 10, "amount": "10.5", "status": " NEW "},
        {"order_id": 1, "customer_id": 10, "amount": 11, "status": "processing"},
    ]
    df = transform(rows)
    assert len(df) == 1
    assert float(df.iloc[0]["amount"]) == 11.0
    assert df.iloc[0]["status"] == "processing"


def test_transform_rejects_invalid_rows():
    rows = [{"order_id": 1, "customer_id": 10, "amount": "-10.5", "status": " NEW "}]

    with pytest.raises(TransformationError):
        transform(rows)
