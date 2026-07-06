import json
from sqlalchemy.orm import Session

from app import models
from app.llm_client import get_diagnosis


def process_alertmanager_payload(payload: dict, db: Session) -> list[models.Incident]:
    """
    Alertmanager sends a payload shaped like:
    {
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "PodCrashLooping", "pod": "watcher-app-xyz", ...},
                "annotations": {"summary": "...", "description": "..."},
                ...
            },
            ...
        ]
    }

    One webhook call can contain MULTIPLE alerts, so we create one Incident per alert.
    """
    alerts = payload.get("alerts", [])
    created_incidents = []

    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        alert_name = labels.get("alertname", "unknown_alert")
        details = json.dumps({"labels": labels, "annotations": annotations})

        diagnosis = get_diagnosis(alert_name, details)

        incident = models.Incident(
            alert_name=alert_name,
            raw_payload=details,
            diagnosis=diagnosis,
            action_taken="alerted_only",  # for now; remediation logic comes later
            outcome=None,
        )
        db.add(incident)
        created_incidents.append(incident)

    db.commit()
    for incident in created_incidents:
        db.refresh(incident)

    return created_incidents
