import pytest
from pydantic import ValidationError

from packages.config import Settings


def test_production_rejects_memory_store() -> None:
    with pytest.raises(ValidationError):
        Settings(env="production", incident_store="memory")


def test_production_accepts_sql_store() -> None:
    settings = Settings(
        env="production",
        incident_store="sql",
        database_url="postgresql+psycopg://example.invalid/aegis",
    )
    assert settings.incident_store == "sql"
    assert not settings.autoremediation_enabled
