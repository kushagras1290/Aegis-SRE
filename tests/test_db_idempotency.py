from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from packages.db.idempotency import process_once
from packages.db.models import Base, ProcessedEvent


def test_process_once() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        calls: list[int] = []
        with Session(engine) as session:
            assert process_once(
                session,
                consumer_name="c",
                event_id="evt_123456",
                handler=lambda: calls.append(1),
            )
            session.commit()
        with Session(engine) as session:
            assert not process_once(
                session,
                consumer_name="c",
                event_id="evt_123456",
                handler=lambda: calls.append(2),
            )
            assert session.scalar(select(ProcessedEvent)) is not None
        assert calls == [1]
    finally:
        engine.dispose()
