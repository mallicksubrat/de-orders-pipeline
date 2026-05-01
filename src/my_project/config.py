from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy.engine import make_url

from my_project.exceptions import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = PROJECT_ROOT / "configs"


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "my_de_project"
    env: str = "dev"
    log_level: str = "INFO"


class PipelineSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_size: int = Field(default=1000, ge=1)


class SourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = "data/raw/orders.json"
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retries: int = Field(default=3, ge=0, le=10)
    backoff_seconds: float = Field(default=1.0, ge=0.0, le=60.0)
    verify_ssl: bool = True
    auth_header: str | None = None
    auth_token: str | None = None


class WarehouseSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    db_url: str = "sqlite:///data/processed/warehouse.db"
    table_name: str = "orders"
    if_exists: str = "replace"
    artifact_path: Path = Path("data/processed/orders.parquet")

    @field_validator("if_exists")
    @classmethod
    def _validate_if_exists(cls, value: str) -> str:
        allowed = {"fail", "replace", "append"}
        if value not in allowed:
            raise ValueError(f"if_exists must be one of {sorted(allowed)}")
        return value

    @field_validator("table_name")
    @classmethod
    def _validate_table_name(cls, value: str) -> str:
        parts = value.split(".")
        if not 1 <= len(parts) <= 2 or any(not part.isidentifier() for part in parts):
            raise ValueError("table_name must be a table or schema.table identifier")
        return value


class ObservabilitySettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lineage_path: Path = Path("data/processed/lineage.jsonl")


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: AppSettings
    pipeline: PipelineSettings
    source: SourceSettings
    warehouse: WarehouseSettings
    observability: ObservabilitySettings

    def resolve_path(self, path: Path) -> Path:
        return path if path.is_absolute() else PROJECT_ROOT / path

    def resolve_database_url(self, db_url: str | None = None) -> str:
        candidate = db_url or self.warehouse.db_url
        prefix = "sqlite:///"
        if candidate.startswith(prefix):
            raw_path = Path(candidate.removeprefix(prefix))
            return f"{prefix}{self.resolve_path(raw_path)}"
        return candidate

    def redacted_dump(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        payload["source"]["auth_token"] = _redact_secret(payload["source"].get("auth_token"))
        payload["source"]["url"] = sanitize_url(payload["source"]["url"])
        payload["warehouse"]["db_url"] = redact_database_url(payload["warehouse"]["db_url"])
        return payload


SENSITIVE_QUERY_KEYS = {
    "access_token",
    "api_key",
    "auth",
    "client_secret",
    "key",
    "password",
    "secret",
    "sig",
    "signature",
    "token",
}


def _redact_secret(value: str | None) -> str | None:
    return None if value is None else "[REDACTED]"


def sanitize_url(value: str) -> str:
    parsed = urlsplit(value)
    if not parsed.query:
        return value

    sanitized_pairs = [
        (key, "[REDACTED]" if key.lower() in SENSITIVE_QUERY_KEYS else item_value)
        for key, item_value in parse_qsl(parsed.query, keep_blank_values=True)
    ]
    return urlunsplit(parsed._replace(query=urlencode(sanitized_pairs)))


def redact_database_url(value: str) -> str:
    try:
        return make_url(value).render_as_string(hide_password=True)
    except Exception:
        return "[INVALID DATABASE URL]"


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _set_nested_value(payload: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current = payload
    for key in path[:-1]:
        current = current.setdefault(key, {})
    current[path[-1]] = value


def _normalize_config_shape(raw: dict[str, Any], env: str) -> dict[str, Any]:
    normalized = {
        "app": {
            "name": raw.get("app_name", "my_de_project"),
            "env": env,
            "log_level": raw.get("log_level", "INFO"),
        },
        "pipeline": {
            "batch_size": raw.get("batch_size", 1000),
        },
        "source": {
            "url": raw.get("source_api", "data/raw/orders.json"),
            "timeout_seconds": raw.get("source_timeout_seconds", 30),
            "retries": raw.get("source_retries", 3),
            "backoff_seconds": raw.get("source_backoff_seconds", 1.0),
            "verify_ssl": raw.get("source_verify_ssl", True),
            "auth_header": raw.get("source_auth_header"),
            "auth_token": raw.get("source_auth_token"),
        },
        "warehouse": {
            "db_url": raw.get("warehouse_url", "sqlite:///data/processed/warehouse.db"),
            "table_name": raw.get("warehouse_table", "orders"),
            "if_exists": raw.get("warehouse_if_exists", "replace"),
            "artifact_path": raw.get("warehouse_artifact_path", "data/processed/orders.parquet"),
        },
        "observability": {
            "lineage_path": raw.get("lineage_path", "data/processed/lineage.jsonl"),
        },
    }

    for section in ("app", "pipeline", "source", "warehouse", "observability"):
        if section in raw:
            normalized[section] = _merge_dicts(normalized[section], raw[section])

    return normalized


def _apply_environment_overrides(payload: dict[str, Any]) -> dict[str, Any]:
    overrides = {
        ("app", "name"): os.getenv("APP_NAME"),
        ("app", "log_level"): os.getenv("LOG_LEVEL"),
        ("source", "url"): os.getenv("SOURCE_URL"),
        ("source", "timeout_seconds"): os.getenv("SOURCE_TIMEOUT_SECONDS"),
        ("source", "retries"): os.getenv("SOURCE_RETRIES"),
        ("source", "backoff_seconds"): os.getenv("SOURCE_BACKOFF_SECONDS"),
        ("source", "verify_ssl"): os.getenv("SOURCE_VERIFY_SSL"),
        ("source", "auth_header"): os.getenv("SOURCE_AUTH_HEADER"),
        ("source", "auth_token"): os.getenv("SOURCE_AUTH_TOKEN"),
        ("warehouse", "db_url"): os.getenv("WAREHOUSE_DB_URL"),
        ("warehouse", "table_name"): os.getenv("WAREHOUSE_TABLE_NAME"),
        ("warehouse", "if_exists"): os.getenv("WAREHOUSE_IF_EXISTS"),
        ("warehouse", "artifact_path"): os.getenv("WAREHOUSE_ARTIFACT_PATH"),
        ("observability", "lineage_path"): os.getenv("LINEAGE_PATH"),
    }

    merged = dict(payload)
    for path, value in overrides.items():
        if value is not None:
            _set_nested_value(merged, path, value)
    return merged


def load_config(env: str | None = None) -> AppConfig:
    active_env = env or os.getenv("APP_ENV", "dev")

    with (CONFIG_ROOT / "base.yaml").open("r", encoding="utf-8") as handle:
        base = yaml.safe_load(handle) or {}

    env_file = CONFIG_ROOT / f"{active_env}.yaml"
    override: dict[str, Any] = {}
    if env_file.exists():
        with env_file.open("r", encoding="utf-8") as handle:
            override = yaml.safe_load(handle) or {}

    merged = _merge_dicts(base, override)
    normalized = _normalize_config_shape(merged, active_env)
    normalized = _apply_environment_overrides(normalized)

    try:
        return AppConfig.model_validate(normalized)
    except ValidationError as exc:
        raise ConfigError(f"Invalid configuration for env '{active_env}': {exc}") from exc
