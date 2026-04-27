from __future__ import annotations

from datetime import datetime, timezone

from my_project.config import AppConfig
from my_project.extractors.orders_api import fetch_orders
from my_project.lineage.emitter import emit_lineage
from my_project.loaders.warehouse import load_df, write_parquet_snapshot
from my_project.models.pipeline import PipelineResult
from my_project.observability.metrics import (
    record_orders_extracted,
    record_pipeline_run,
    record_rows_loaded,
)
from my_project.quality.orders import validate_orders
from my_project.transformers.clean_orders import transform
from my_project.utils.logger import get_logger


def run_orders_pipeline(config: AppConfig) -> PipelineResult:
    logger = get_logger("my_project.pipeline", level=config.app.log_level)
    logger.info("Starting pipeline app=%s env=%s", config.app.name, config.app.env)

    try:
        raw_rows = fetch_orders(config.source)
        bounded_rows = raw_rows[: config.pipeline.batch_size]
        record_orders_extracted(len(bounded_rows))

        transformed = transform(bounded_rows)
        validate_orders(transformed)

        artifact_path = None
        if not transformed.empty:
            artifact_path = write_parquet_snapshot(
                transformed,
                config.resolve_path(config.warehouse.artifact_path),
            )

        loaded_rows = load_df(
            transformed,
            table_name=config.warehouse.table_name,
            db_url=config.resolve_database_url(),
            if_exists=config.warehouse.if_exists,
        )
        record_rows_loaded(loaded_rows)

        lineage_path = config.resolve_path(config.observability.lineage_path)
        event = {
            "event_type": "orders_pipeline_completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": config.app.env,
            "source_url": config.source.url,
            "warehouse_table": config.warehouse.table_name,
            "extracted_rows": len(bounded_rows),
            "transformed_rows": int(len(transformed)),
            "loaded_rows": loaded_rows,
            "artifact_path": str(artifact_path) if artifact_path else None,
        }
        emit_lineage(event, output_path=lineage_path)
        record_pipeline_run("success")

        logger.info("Pipeline finished loaded_rows=%s", loaded_rows)
        return PipelineResult(
            extracted_rows=len(bounded_rows),
            transformed_rows=int(len(transformed)),
            loaded_rows=loaded_rows,
            warehouse_table=config.warehouse.table_name,
            artifact_path=artifact_path,
            lineage_path=lineage_path,
        )
    except Exception:
        record_pipeline_run("failure")
        logger.exception("Pipeline execution failed")
        raise
