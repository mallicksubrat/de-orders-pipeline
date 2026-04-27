from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from my_project.exceptions import LoadError


def _prepare_sqlite_target(db_url: str) -> None:
    prefix = "sqlite:///"
    if db_url.startswith(prefix):
        db_path = Path(db_url.removeprefix(prefix))
        if not db_path.is_absolute():
            db_path = Path.cwd() / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)


def _split_table_name(table_name: str) -> tuple[str | None, str]:
    if "." not in table_name:
        return None, table_name
    schema, table = table_name.split(".", maxsplit=1)
    return schema, table


def _ensure_schema(connection: Connection, schema: str | None) -> None:
    if schema and connection.dialect.name == "postgresql":
        connection.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')


def load_df(df, table_name: str, db_url: str, if_exists: str = "append") -> int:
    if df.empty:
        return 0

    _prepare_sqlite_target(db_url)
    schema, resolved_table = _split_table_name(table_name)
    engine = create_engine(db_url, future=True, pool_pre_ping=True)

    try:
        with engine.begin() as connection:
            _ensure_schema(connection, schema)
            df.to_sql(
                resolved_table,
                con=connection,
                schema=schema,
                if_exists=if_exists,
                index=False,
            )
    except Exception as exc:
        raise LoadError(f"Failed to load dataframe into {table_name}: {exc}") from exc
    finally:
        engine.dispose()

    return int(len(df))


def write_parquet_snapshot(df, artifact_path: Path) -> Path:
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(artifact_path, index=False)
    return artifact_path
