from prometheus_client import Counter

pipeline_runs = Counter(
    "orders_pipeline_runs_total",
    "Number of pipeline executions by status.",
    ["status"],
)
orders_extracted = Counter("orders_extracted_total", "Rows extracted from the source.")
rows_loaded = Counter("rows_loaded_total", "Rows loaded into the warehouse.")


def record_pipeline_run(status: str) -> None:
    pipeline_runs.labels(status=status).inc()


def record_orders_extracted(count: int) -> None:
    if count > 0:
        orders_extracted.inc(count)


def record_rows_loaded(count: int) -> None:
    if count > 0:
        rows_loaded.inc(count)
