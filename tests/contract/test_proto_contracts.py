from pathlib import Path


def test_protobuf_contracts_are_versioned_and_tenant_aware() -> None:
    telemetry = Path("schemas/protobuf/telemetry.proto").read_text(encoding="utf-8")
    anomaly = Path("schemas/protobuf/anomaly.proto").read_text(encoding="utf-8")
    assert "schema_version" in telemetry
    assert "organization_id" in telemetry
    assert "organization_id" in anomaly
    assert "event_id" in telemetry
