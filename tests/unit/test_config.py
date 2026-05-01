from my_project.config import AppConfig, load_config, sanitize_url


def test_load_config_uses_nested_settings():
    config = load_config(env="dev")

    assert config.app.name == "my_de_project"
    assert config.app.env == "dev"
    assert config.source.url == "data/raw/orders.json"
    assert config.source.retries == 3
    assert config.warehouse.table_name == "orders"


def test_redacted_dump_masks_sensitive_values():
    config = AppConfig.model_validate(
        {
            "app": {"name": "test-project", "env": "test", "log_level": "INFO"},
            "pipeline": {"batch_size": 100},
            "source": {
                "url": "https://example.test/orders?token=dummy-token-value&region=us",
                "timeout_seconds": 5,
                "retries": 1,
                "backoff_seconds": 0.1,
                "verify_ssl": True,
                "auth_token": "dummy-token-value",
            },
            "warehouse": {
                "db_url": "postgresql+psycopg2://user:dummy-password@host:5432/db",
                "table_name": "analytics.orders",
                "if_exists": "append",
                "artifact_path": "data/processed/orders.parquet",
            },
            "observability": {"lineage_path": "data/processed/lineage.jsonl"},
        }
    )

    redacted = config.redacted_dump()

    assert redacted["source"]["auth_token"] == "[REDACTED]"
    assert "dummy-token-value" not in redacted["source"]["url"]
    assert "dummy-password" not in redacted["warehouse"]["db_url"]


def test_sanitize_url_redacts_sensitive_query_params():
    sanitized = sanitize_url("https://example.test/orders?api_key=abc123&region=us")

    assert sanitized == "https://example.test/orders?api_key=%5BREDACTED%5D&region=us"
