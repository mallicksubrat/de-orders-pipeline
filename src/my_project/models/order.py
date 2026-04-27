from pydantic import BaseModel, ConfigDict, Field, field_validator


class Order(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    order_id: int
    customer_id: int
    amount: float = Field(ge=0)
    status: str

    @field_validator("amount", mode="before")
    @classmethod
    def _coerce_amount(cls, value):
        if value is None or value == "":
            raise ValueError("amount is required")
        return float(value)

    @field_validator("status")
    @classmethod
    def _normalize_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("status cannot be empty")
        return normalized
