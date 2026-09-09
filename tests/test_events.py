from datetime import UTC, datetime
import pytest
from pydantic import ValidationError
from packages.contracts.events import EventEnvelope
def valid(): return dict(event_id='evt_123456',event_type='telemetry.metric.v1',schema_version=1,occurred_at=datetime.now(UTC),organization_id='org',environment='production',source='otel')
def test_event_valid(): assert EventEnvelope(**valid()).schema_version==1
def test_naive_rejected():
 d=valid(); d['occurred_at']=datetime.now();
 with pytest.raises(ValidationError): EventEnvelope(**d)
def test_type_versioned():
 d=valid(); d['event_type']='metric';
 with pytest.raises(ValidationError): EventEnvelope(**d)
