from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class IncidentStatus(StrEnum):
    DETECTED="DETECTED"
    TRIAGED="TRIAGED"
    INVESTIGATING="INVESTIGATING"
    NEEDS_HUMAN="NEEDS_HUMAN"
    CAUSE_IDENTIFIED="CAUSE_IDENTIFIED"
    REMEDIATION_PROPOSED="REMEDIATION_PROPOSED"
    AWAITING_APPROVAL="AWAITING_APPROVAL"
    REJECTED="REJECTED"
    REMEDIATING="REMEDIATING"
    REMEDIATION_FAILED="REMEDIATION_FAILED"
    VERIFYING="VERIFYING"
    STILL_DEGRADED="STILL_DEGRADED"
    RESOLVED="RESOLVED"
    POSTMORTEM_COMPLETE="POSTMORTEM_COMPLETE"
    CLOSED="CLOSED"

class Severity(StrEnum):
    SEV1="SEV-1"; SEV2="SEV-2"; SEV3="SEV-3"; SEV4="SEV-4"

class Incident(BaseModel):
    id: UUID=Field(default_factory=uuid4)
    organization_id: str=Field(min_length=1, max_length=128)
    environment: str=Field(min_length=1, max_length=64)
    title: str=Field(min_length=3, max_length=300)
    status: IncidentStatus=IncidentStatus.DETECTED
    severity: Severity=Severity.SEV3
    primary_service: str|None=None
    detected_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int=0
    @field_validator('detected_at')
    @classmethod
    def tz_required(cls,v:datetime)->datetime:
        if v.tzinfo is None: raise ValueError('detected_at must be timezone-aware')
        return v.astimezone(timezone.utc)

class IncidentTransition(BaseModel):
    incident_id: UUID
    from_status: IncidentStatus
    to_status: IncidentStatus
    actor: str
    reason: str
    occurred_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
