from __future__ import annotations

from typing import Protocol
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from packages.config import Settings, get_settings
from packages.db.incident_repository import ConcurrencyConflict, IncidentNotFound, IncidentPage, SQLIncidentRepository
from packages.db.models import Base
from packages.domain.models import Incident, IncidentStatus, IncidentTransition
from packages.domain.service import InMemoryIncidentService, SQLIncidentService
from packages.domain.state_machine import InvalidIncidentTransition


class IncidentService(Protocol):
    def create(self, incident: Incident) -> Incident: ...
    def get(self, organization_id: str, incident_id: UUID) -> Incident: ...
    def list(
        self,
        organization_id: str,
        *,
        limit: int,
        cursor: str | None = None,
    ) -> IncidentPage: ...
    def move(
        self,
        organization_id: str,
        incident_id: UUID,
        target: IncidentStatus,
        *,
        actor: str,
        reason: str,
        expected_version: int,
    ) -> Incident: ...
    def timeline(self, organization_id: str, incident_id: UUID) -> list[IncidentTransition]: ...


class TransitionRequest(BaseModel):
    target: IncidentStatus
    actor: str = Field(min_length=1, max_length=128)
    reason: str = Field(min_length=1, max_length=1000)
    expected_version: int = Field(ge=0)


class IncidentListResponse(BaseModel):
    items: list[Incident]
    next_cursor: str | None = None


def _build_service(settings: Settings) -> IncidentService:
    if settings.incident_store == "memory":
        return InMemoryIncidentService()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine, expire_on_commit=False, class_=Session)
    return SQLIncidentService(SQLIncidentRepository(sessions))


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    app = FastAPI(title="Aegis SRE API", version="0.1.0")
    app.state.settings = resolved
    app.state.incidents = _build_service(resolved)

    def get_service(request: Request) -> IncidentService:
        service: IncidentService = request.app.state.incidents
        return service

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready() -> dict[str, str]:
        return {"status": "ready"}

    @app.post("/api/v1/incidents", response_model=Incident, status_code=201)
    def create_incident(
        incident: Incident,
        request: Request,
    ) -> Incident:
        return get_service(request).create(incident)

    @app.get("/api/v1/incidents", response_model=IncidentListResponse)
    def list_incidents(
        request: Request,
        organization_id: str,
        limit: int = Query(default=50, ge=1, le=resolved.page_size_max),
        cursor: str | None = None,
    ) -> IncidentListResponse:
        page = get_service(request).list(organization_id, limit=limit, cursor=cursor)
        return IncidentListResponse(items=page.items, next_cursor=page.next_cursor)

    @app.get("/api/v1/incidents/{incident_id}", response_model=Incident)
    def get_incident(
        incident_id: UUID,
        organization_id: str,
        request: Request,
    ) -> Incident:
        try:
            return get_service(request).get(organization_id, incident_id)
        except IncidentNotFound as exc:
            raise HTTPException(404, "incident not found") from exc

    @app.get(
        "/api/v1/incidents/{incident_id}/timeline",
        response_model=list[IncidentTransition],
    )
    def get_timeline(
        incident_id: UUID,
        organization_id: str,
        request: Request,
    ) -> list[IncidentTransition]:
        try:
            return get_service(request).timeline(organization_id, incident_id)
        except IncidentNotFound as exc:
            raise HTTPException(404, "incident not found") from exc

    @app.post("/api/v1/incidents/{incident_id}/transition", response_model=Incident)
    def move(
        incident_id: UUID,
        organization_id: str,
        transition_request: TransitionRequest,
        request: Request,
    ) -> Incident:
        try:
            return get_service(request).move(
                organization_id,
                incident_id,
                transition_request.target,
                actor=transition_request.actor,
                reason=transition_request.reason,
                expected_version=transition_request.expected_version,
            )
        except IncidentNotFound as exc:
            raise HTTPException(404, "incident not found") from exc
        except InvalidIncidentTransition as exc:
            raise HTTPException(409, str(exc)) from exc
        except ConcurrencyConflict as exc:
            raise HTTPException(409, "incident version conflict") from exc

    return app


app = create_app()
