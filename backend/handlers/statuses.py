from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.db import schema
from service.db.db import get_db
from service.db.service import StatusService

router = APIRouter(prefix="/statuses", tags=["statuses"])


@router.post("/", response_model=schema.Status, status_code=status.HTTP_201_CREATED)
def create_status(
    status_in: schema.StatusCreate, db: Session = Depends(get_db)
) -> schema.Status:
    service = StatusService(db)
    status_obj = service.create_status(status_in)
    return schema.Status.model_validate(status_obj)


@router.get("/", response_model=List[schema.Status])
def list_statuses(db: Session = Depends(get_db)) -> List[schema.Status]:
    service = StatusService(db)
    statuses = service.list_statuses()
    return [schema.Status.model_validate(item) for item in statuses]


@router.get("/{status_id}", response_model=schema.Status)
def get_status(status_id: int, db: Session = Depends(get_db)) -> schema.Status:
    service = StatusService(db)
    status_obj = service.get_status(status_id)
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return schema.Status.model_validate(status_obj)


@router.put("/{status_id}", response_model=schema.Status)
def update_status(
    status_id: int, status_in: schema.StatusUpdate, db: Session = Depends(get_db)
) -> schema.Status:
    service = StatusService(db)
    status_obj = service.update_status(status_id, status_in)
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return schema.Status.model_validate(status_obj)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(status_id: int, db: Session = Depends(get_db)) -> None:
    service = StatusService(db)
    deleted = service.delete_status(status_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

