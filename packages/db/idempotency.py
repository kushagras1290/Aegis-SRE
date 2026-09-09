from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.db.models import ProcessedEvent


def process_once(
    session: Session,
    *,
    consumer_name: str,
    event_id: str,
    handler: Callable[[], None],
) -> bool:
    existing = session.scalar(
        select(ProcessedEvent).where(
            ProcessedEvent.consumer_name == consumer_name,
            ProcessedEvent.event_id == event_id,
        )
    )
    if existing is not None:
        return False
    handler()
    session.add(ProcessedEvent(consumer_name=consumer_name, event_id=event_id))
    session.flush()
    return True
