from datetime import datetime
from pydantic import BaseModel


class IncidentCreate(BaseModel):
    alert_name: str
    raw_payload: str | None = None


class IncidentResponse(BaseModel):
    id: int
    alert_name: str
    raw_payload: str | None
    diagnosis: str | None
    action_taken: str | None
    outcome: str | None
    created_at: datetime

    class Config:
        from_attributes = True  # lets Pydantic read directly from SQLAlchemy objects
