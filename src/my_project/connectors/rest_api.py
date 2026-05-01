from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from my_project.config import sanitize_url
from my_project.exceptions import DataSourceError

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _validate_http_response(response: Response) -> dict | list:
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        raise DataSourceError(
            f"Source request failed with status {response.status_code}: {response.text[:200]}"
        ) from exc
    except ValueError as exc:
        raise DataSourceError("Source response was not valid JSON.") from exc


def _load_local_json(url: str) -> dict | list:
    parsed = urlparse(url)
    raw_path = Path(parsed.path if parsed.scheme == "file" else url)
    file_path = raw_path if raw_path.is_absolute() else PROJECT_ROOT / raw_path

    if not file_path.exists():
        raise DataSourceError(f"Local source file does not exist: {file_path}")

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataSourceError(f"Local source file is not valid JSON: {file_path}") from exc


def _build_session(retries: int, backoff_seconds: float) -> requests.Session:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        allowed_methods=("GET",),
        backoff_factor=backoff_seconds,
        status_forcelist=(429, 500, 502, 503, 504),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_json(
    url: str,
    timeout: int = 30,
    session: requests.Session | None = None,
    retries: int = 3,
    backoff_seconds: float = 1.0,
    verify_ssl: bool = True,
    auth_header: str | None = None,
    auth_token: str | None = None,
) -> dict | list:
    parsed = urlparse(url)
    if parsed.scheme in {"", "file"}:
        return _load_local_json(url)

    client = session or _build_session(retries, backoff_seconds)
    headers = {"Accept": "application/json"}
    if auth_header and auth_token:
        headers[auth_header] = auth_token
    try:
        response = client.get(url, timeout=timeout, headers=headers, verify=verify_ssl)
    except requests.RequestException as exc:
        raise DataSourceError(f"Source request failed for {sanitize_url(url)}: {exc}") from exc
    return _validate_http_response(response)
