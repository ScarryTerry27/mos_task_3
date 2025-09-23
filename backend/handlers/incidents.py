from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.db import schema
from service.db.db import get_db
from service.db.service import IncidentService

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/", response_model=schema.Incident, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_in: schema.IncidentCreate, db: Session = Depends(get_db)
) -> schema.Incident:
    service = IncidentService(db)
    incident = service.create_incident(incident_in)
    return schema.Incident.model_validate(incident)


@router.get("/", response_model=List[schema.Incident])
def list_incidents(db: Session = Depends(get_db)) -> List[schema.Incident]:
    service = IncidentService(db)
    incidents = service.list_incidents()
    return [schema.Incident.model_validate(item) for item in incidents]


@router.get("/{incident_id}", response_model=schema.Incident)
def get_incident(incident_id: int, db: Session = Depends(get_db)) -> schema.Incident:
    service = IncidentService(db)
    incident = service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return schema.Incident.model_validate(incident)


@router.put("/{incident_id}", response_model=schema.Incident)
def update_incident(
    incident_id: int, incident_in: schema.IncidentBase, db: Session = Depends(get_db)
) -> schema.Incident:
    service = IncidentService(db)
    incident = service.update_incident(incident_id, incident_in)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return schema.Incident.model_validate(incident)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)) -> None:
    service = IncidentService(db)
    deleted = service.delete_incident(incident_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

