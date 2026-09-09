from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from packages.db.incident_repository import ConcurrencyConflict, SQLIncidentRepository
from packages.db.models import Base
from packages.domain.models import Incident, IncidentStatus
from packages.domain.service import SQLIncidentService


def service() -> tuple[SQLIncidentService, object]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine, expire_on_commit=False, class_=Session)
    return SQLIncidentService(SQLIncidentRepository(sessions)), engine


def test_sql_round_trip_and_timeline() -> None:
    svc, engine = service()
    try:
        incident = Incident(organization_id="org", environment="production", title="checkout failure")
        svc.create(incident)
        loaded = svc.get("org", incident.id)
        assert loaded.detected_at.tzinfo is not None
        moved = svc.move("org", incident.id, IncidentStatus.TRIAGED, actor="alice", reason="ack", expected_version=0)
        assert moved.version == 1
        timeline = svc.timeline("org", incident.id)
        assert len(timeline) == 1
        assert timeline[0].actor == "alice"
    finally:
        engine.dispose()


def test_sql_optimistic_concurrency() -> None:
    svc, engine = service()
    try:
        incident = Incident(organization_id="org", environment="production", title="checkout failure")
        svc.create(incident)
        svc.move("org", incident.id, IncidentStatus.TRIAGED, actor="alice", reason="ack", expected_version=0)
        try:
            svc.move("org", incident.id, IncidentStatus.INVESTIGATING, actor="bob", reason="stale", expected_version=0)
        except ConcurrencyConflict:
            pass
        else:
            raise AssertionError("expected concurrency conflict")
    finally:
        engine.dispose()


def test_sql_cursor_pagination_is_tenant_scoped() -> None:
    svc, engine = service()
    try:
        for org in ("a", "a", "a", "b"):
            svc.create(Incident(organization_id=org, environment="prod", title="incident"))
        first = svc.list("a", limit=2)
        assert len(first.items) == 2
        assert first.next_cursor is not None
        second = svc.list("a", limit=2, cursor=first.next_cursor)
        assert len(second.items) == 1
        assert all(item.organization_id == "a" for item in first.items + second.items)
    finally:
        engine.dispose()
