from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, and_, select, update
from sqlalchemy.orm import Session, sessionmaker

from packages.db.models import IncidentRecord, IncidentTransitionRecord
from packages.domain.models import Incident, IncidentStatus, IncidentTransition, Severity


class IncidentNotFound(LookupError):
    pass


class ConcurrencyConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class IncidentPage:
    items: list[Incident]
    next_cursor: str | None


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _to_domain(row: IncidentRecord) -> Incident:
    return Incident(
        id=UUID(row.id),
        organization_id=row.organization_id,
        environment=row.environment,
        title=row.title,
        status=IncidentStatus(row.status),
        severity=Severity(row.severity),
        primary_service=row.primary_service,
        detected_at=_utc(row.detected_at),
        version=row.version,
    )


class SQLIncidentRepository:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def create(self, incident: Incident) -> Incident:
        with self._sessions.begin() as session:
            session.add(
                IncidentRecord(
                    id=str(incident.id),
                    organization_id=incident.organization_id,
                    environment=incident.environment,
                    title=incident.title,
                    status=incident.status.value,
                    severity=incident.severity.value,
                    primary_service=incident.primary_service,
                    detected_at=incident.detected_at,
                    version=incident.version,
                )
            )
        return incident.model_copy(deep=True)

    def get(self, organization_id: str, incident_id: UUID) -> Incident:
        with self._sessions() as session:
            row = session.scalar(
                select(IncidentRecord).where(
                    and_(
                        IncidentRecord.id == str(incident_id),
                        IncidentRecord.organization_id == organization_id,
                    )
                )
            )
            if row is None:
                raise IncidentNotFound(str(incident_id))
            return _to_domain(row)

    def list(
        self,
        organization_id: str,
        *,
        limit: int,
        cursor: str | None = None,
    ) -> IncidentPage:
        statement: Select[tuple[IncidentRecord]] = select(IncidentRecord).where(
            IncidentRecord.organization_id == organization_id
        )
        if cursor is not None:
            statement = statement.where(IncidentRecord.id > cursor)
        statement = statement.order_by(IncidentRecord.id.asc()).limit(limit + 1)
        with self._sessions() as session:
            rows = list(session.scalars(statement))
        has_more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = rows[-1].id if has_more and rows else None
        return IncidentPage([_to_domain(row) for row in rows], next_cursor)

    def apply_transition(
        self,
        incident: Incident,
        transition: IncidentTransition,
        *,
        expected_version: int,
    ) -> Incident:
        if incident.version != expected_version + 1:
            raise ValueError("incident version must advance exactly once")
        with self._sessions.begin() as session:
            result = session.execute(
                update(IncidentRecord)
                .where(
                    and_(
                        IncidentRecord.id == str(incident.id),
                        IncidentRecord.organization_id == incident.organization_id,
                        IncidentRecord.version == expected_version,
                    )
                )
                .values(status=incident.status.value, version=incident.version)
            )
            if result.rowcount != 1:
                raise ConcurrencyConflict(str(incident.id))
            session.add(
                IncidentTransitionRecord(
                    incident_id=str(incident.id),
                    organization_id=incident.organization_id,
                    from_status=transition.from_status.value,
                    to_status=transition.to_status.value,
                    actor=transition.actor,
                    reason=transition.reason,
                    occurred_at=transition.occurred_at,
                )
            )
        return incident.model_copy(deep=True)

    def timeline(self, organization_id: str, incident_id: UUID) -> list[IncidentTransition]:
        with self._sessions() as session:
            rows = list(
                session.scalars(
                    select(IncidentTransitionRecord)
                    .where(
                        and_(
                            IncidentTransitionRecord.incident_id == str(incident_id),
                            IncidentTransitionRecord.organization_id == organization_id,
                        )
                    )
                    .order_by(IncidentTransitionRecord.id.asc())
                )
            )
        return [
            IncidentTransition(
                incident_id=incident_id,
                from_status=IncidentStatus(row.from_status),
                to_status=IncidentStatus(row.to_status),
                actor=row.actor,
                reason=row.reason,
                occurred_at=_utc(row.occurred_at),
            )
            for row in rows
        ]
