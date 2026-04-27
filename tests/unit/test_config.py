from my_project.config import load_config


def test_load_config_uses_nested_settings():
    config = load_config(env="dev")

    assert config.app.name == "my_de_project"
    assert config.app.env == "dev"
    assert config.source.url == "data/raw/orders.json"
    assert config.source.retries == 3
    assert config.warehouse.table_name == "orders"
