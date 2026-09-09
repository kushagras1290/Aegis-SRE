from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraceContext:
    request_id: str | None = None
    trace_id: str | None = None
    incident_id: str | None = None
    event_id: str | None = None
    organization_id: str | None = None


_current: ContextVar[TraceContext] = ContextVar("aegis_trace_context", default=TraceContext())


def set_trace_context(context: TraceContext) -> None:
    _current.set(context)


def get_trace_context() -> TraceContext:
    return _current.get()
