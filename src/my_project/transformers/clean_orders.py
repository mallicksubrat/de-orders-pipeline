import pandas as pd
from pydantic import ValidationError

from my_project.exceptions import TransformationError
from my_project.models.order import Order

ORDER_COLUMNS = ["order_id", "customer_id", "amount", "status"]


def transform(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    cleaned_rows: list[dict] = []
    for index, row in enumerate(rows):
        try:
            cleaned_rows.append(Order.model_validate(row).model_dump())
        except ValidationError as exc:
            raise TransformationError(f"Invalid order payload at position {index}: {exc}") from exc

    df = pd.DataFrame(cleaned_rows)
    df = df.sort_values("order_id").drop_duplicates(subset=["order_id"], keep="last")
    df = df.reset_index(drop=True)
    return df[ORDER_COLUMNS]
