from __future__ import annotations

from packages.contracts.events import EventEnvelope
from packages.telemetry.normalize import normalize


def normalize_event(event: EventEnvelope) -> dict[str, object]:
    payload = normalize(
        {
            "timestamp": event.occurred_at,
            "organization_id": event.organization_id,
            "environment": event.environment,
            **event.payload,
        }
    )
    payload["event_id"] = event.event_id
    payload["event_type"] = event.event_type
    payload["schema_version"] = event.schema_version
    return payload
