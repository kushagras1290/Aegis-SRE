from __future__ import annotations

from threading import RLock
from uuid import UUID

from packages.db.incident_repository import IncidentNotFound, IncidentPage, SQLIncidentRepository
from packages.domain.models import Incident, IncidentStatus, IncidentTransition
from packages.domain.state_machine import transition


class InMemoryIncidentService:
    def __init__(self) -> None:
        self._incidents: dict[str, Incident] = {}
        self._timeline: dict[str, list[IncidentTransition]] = {}
        self._lock = RLock()

    def create(self, incident: Incident) -> Incident:
        with self._lock:
            self._incidents[str(incident.id)] = incident.model_copy(deep=True)
        return incident.model_copy(deep=True)

    def get(self, organization_id: str, incident_id: UUID) -> Incident:
        with self._lock:
            incident = self._incidents.get(str(incident_id))
            if incident is None or incident.organization_id != organization_id:
                raise IncidentNotFound(str(incident_id))
            return incident.model_copy(deep=True)

    def list(
        self,
        organization_id: str,
        *,
        limit: int,
        cursor: str | None = None,
    ) -> IncidentPage:
        with self._lock:
            rows = sorted(
                (
                    item.model_copy(deep=True)
                    for item in self._incidents.values()
                    if item.organization_id == organization_id
                    and (cursor is None or str(item.id) > cursor)
                ),
                key=lambda item: str(item.id),
            )
        has_more = len(rows) > limit
        rows = rows[:limit]
        return IncidentPage(rows, str(rows[-1].id) if has_more and rows else None)

    def move(
        self,
        organization_id: str,
        incident_id: UUID,
        target: IncidentStatus,
        *,
        actor: str,
        reason: str,
        expected_version: int,
    ) -> Incident:
        with self._lock:
            current = self._incidents.get(str(incident_id))
            if current is None or current.organization_id != organization_id:
                raise IncidentNotFound(str(incident_id))
            if current.version != expected_version:
                from packages.db.incident_repository import ConcurrencyConflict

                raise ConcurrencyConflict(str(incident_id))
            working = current.model_copy(deep=True)
            record = transition(working, target, actor=actor, reason=reason)
            self._incidents[str(incident_id)] = working
            self._timeline.setdefault(str(incident_id), []).append(record)
            return working.model_copy(deep=True)

    def timeline(self, organization_id: str, incident_id: UUID) -> list[IncidentTransition]:
        self.get(organization_id, incident_id)
        with self._lock:
            return [item.model_copy(deep=True) for item in self._timeline.get(str(incident_id), [])]


class SQLIncidentService:
    def __init__(self, repository: SQLIncidentRepository) -> None:
        self._repository = repository

    def create(self, incident: Incident) -> Incident:
        return self._repository.create(incident)

    def get(self, organization_id: str, incident_id: UUID) -> Incident:
        return self._repository.get(organization_id, incident_id)

    def list(
        self,
        organization_id: str,
        *,
        limit: int,
        cursor: str | None = None,
    ) -> IncidentPage:
        return self._repository.list(organization_id, limit=limit, cursor=cursor)

    def move(
        self,
        organization_id: str,
        incident_id: UUID,
        target: IncidentStatus,
        *,
        actor: str,
        reason: str,
        expected_version: int,
    ) -> Incident:
        current = self._repository.get(organization_id, incident_id)
        if current.version != expected_version:
            from packages.db.incident_repository import ConcurrencyConflict

            raise ConcurrencyConflict(str(incident_id))
        record = transition(current, target, actor=actor, reason=reason)
        return self._repository.apply_transition(current, record, expected_version=expected_version)

    def timeline(self, organization_id: str, incident_id: UUID) -> list[IncidentTransition]:
        self._repository.get(organization_id, incident_id)
        return self._repository.timeline(organization_id, incident_id)
