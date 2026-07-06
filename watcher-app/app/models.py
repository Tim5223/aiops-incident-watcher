from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    # What triggered this incident (e.g. "pod-crash-loop", "high-cpu")
    alert_name = Column(String, nullable=False)

    # Raw details from Alertmanager, stored as-is for reference
    raw_payload = Column(Text, nullable=True)

    # What the LLM diagnosed as the likely cause
    diagnosis = Column(Text, nullable=True)

    # What action the Watcher took: "alerted_only", "restarted_pod", etc.
    action_taken = Column(String, nullable=True)

    # Free-text outcome/result notes
    outcome = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
