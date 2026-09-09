from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, field_validator

class EventEnvelope(BaseModel):
    event_id:str=Field(min_length=8,max_length=128)
    event_type:str=Field(pattern=r'^[a-z0-9_.-]+\.v[0-9]+$')
    schema_version:int=Field(ge=1)
    occurred_at:datetime
    ingested_at:datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    organization_id:str=Field(min_length=1,max_length=128)
    environment:str=Field(min_length=1,max_length=64)
    source:str=Field(min_length=1,max_length=64)
    trace_id:str|None=None
    correlation_id:str|None=None
    payload:dict[str,Any]=Field(default_factory=dict)
    @field_validator('occurred_at','ingested_at')
    @classmethod
    def utc(cls,v:datetime)->datetime:
        if v.tzinfo is None: raise ValueError('timestamps must be timezone-aware')
        return v.astimezone(timezone.utc)
