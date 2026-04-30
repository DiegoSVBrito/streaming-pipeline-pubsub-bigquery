from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EventMessage(BaseModel):
    event_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    source: str = "unknown"
    payload: Optional[dict] = None
    event_timestamp: datetime
    processed_at: Optional[datetime] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v):
        allowed = {"click", "purchase", "page_view", "signup", "error"}
        if v not in allowed:
            raise ValueError(f"event_type must be one of {allowed}")
        return v
