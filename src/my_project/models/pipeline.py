from pathlib import Path

from pydantic import BaseModel


class PipelineResult(BaseModel):
    extracted_rows: int
    transformed_rows: int
    loaded_rows: int
    warehouse_table: str
    artifact_path: Path | None = None
    lineage_path: Path | None = None
