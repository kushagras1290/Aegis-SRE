from datetime import UTC, datetime

from apps.telemetry_ingestor.processor import normalize_event
from packages.contracts.events import EventEnvelope


def test_ingestor_preserves_event_identity() -> None:
    event = EventEnvelope(
        event_id="evt_123456",
        event_type="telemetry.metric.v1",
        schema_version=1,
        occurred_at=datetime.now(UTC),
        organization_id="org",
        environment="production",
        source="otel",
        payload={"service.name": "checkout"},
    )
    normalized = normalize_event(event)
    assert normalized["tenant_id"] == "org"
    assert normalized["event_id"] == "evt_123456"
