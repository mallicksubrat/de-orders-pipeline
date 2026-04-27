import pandas as pd
import pytest

from my_project.exceptions import DataQualityError
from my_project.quality.orders import validate_orders


def test_validate_orders_rejects_duplicates():
    df = pd.DataFrame(
        [
            {"order_id": 1, "customer_id": 10, "amount": 10.5, "status": "new"},
            {"order_id": 1, "customer_id": 11, "amount": 12.0, "status": "new"},
        ]
    )

    with pytest.raises(DataQualityError):
        validate_orders(df)
