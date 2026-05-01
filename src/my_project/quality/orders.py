import pandas as pd

from my_project.exceptions import DataQualityError

REQUIRED_COLUMNS = ("order_id", "customer_id", "amount", "status")

def validate_orders(df: pd.DataFrame) -> None:
    if df.empty:
        return

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise DataQualityError(f"Orders dataframe is missing required columns: {missing_columns}")

    duplicate_ids = df.loc[df["order_id"].duplicated(), "order_id"].tolist()
    if duplicate_ids:
        raise DataQualityError(
            f"Duplicate order_id values found after transformation: {duplicate_ids}"
        )

    if (df["amount"] < 0).any():
        raise DataQualityError("Order amounts must be non-negative.")

    if df["customer_id"].isna().any():
        raise DataQualityError("customer_id cannot be null.")

    if df["status"].astype(str).str.strip().eq("").any():
        raise DataQualityError("status cannot be blank.")
