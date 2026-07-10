from typing import Any
# CI/CD pipeline test
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, get_db, Base
from app import models, schemas
from app.webhook import process_alertmanager_payload

# Creates the "incidents" table on startup if it doesn't already exist.
# (Fine for now; later we'll switch to Alembic migrations for real schema changes.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIOps Incident Watcher")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Watcher service is alive"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Checks that the app AND the database connection are both working."""
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}


@app.post("/incidents", response_model=schemas.IncidentResponse)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    db_incident = models.Incident(
        alert_name=incident.alert_name,
        raw_payload=incident.raw_payload,
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


@app.get("/incidents", response_model=list[schemas.IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).order_by(models.Incident.created_at.desc()).all()


@app.post("/webhook/alertmanager", response_model=list[schemas.IncidentResponse])
def alertmanager_webhook(payload: dict[str, Any], db: Session = Depends(get_db)):
    """
    Receives Alertmanager's webhook payload, creates an Incident per alert,
    and runs each one through the (currently mocked) LLM diagnosis step.
    """
    incidents = process_alertmanager_payload(payload, db)
    return incidents
