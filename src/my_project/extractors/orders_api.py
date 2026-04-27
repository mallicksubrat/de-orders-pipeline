from __future__ import annotations

from my_project.config import SourceSettings
from my_project.connectors.rest_api import get_json
from my_project.exceptions import DataSourceError


def fetch_orders(source: SourceSettings) -> list[dict]:
    payload = get_json(
        source.url,
        timeout=source.timeout_seconds,
        retries=source.retries,
        backoff_seconds=source.backoff_seconds,
        verify_ssl=source.verify_ssl,
        auth_header=source.auth_header,
        auth_token=source.auth_token,
    )
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("orders"), list):
        return payload["orders"]
    raise DataSourceError("Expected source payload to be a list or an object containing an 'orders' list.")
