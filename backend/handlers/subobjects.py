from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.db import schema
from service.db.db import get_db
from service.db.service import SubObjectService

router = APIRouter(prefix="/subobjects", tags=["subobjects"])


@router.post("/", response_model=schema.SubObjectResponse, status_code=status.HTTP_201_CREATED)
def create_subobject(
    subobject_in: schema.SubObjectCreate, db: Session = Depends(get_db)
) -> schema.SubObjectResponse:
    service = SubObjectService(db)
    subobject = service.create_subobject(subobject_in)
    return schema.SubObjectResponse.model_validate(subobject)


@router.get("/", response_model=List[schema.SubObjectResponse])
def list_subobjects(db: Session = Depends(get_db)) -> List[schema.SubObjectResponse]:
    service = SubObjectService(db)
    subobjects = service.list_subobjects()
    return [schema.SubObjectResponse.model_validate(item) for item in subobjects]


@router.get("/{subobject_id}", response_model=schema.SubObjectResponse)
def get_subobject(subobject_id: int, db: Session = Depends(get_db)) -> schema.SubObjectResponse:
    service = SubObjectService(db)
    subobject = service.get_subobject(subobject_id)
    if not subobject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found")
    return schema.SubObjectResponse.model_validate(subobject)


@router.put("/{subobject_id}", response_model=schema.SubObjectResponse)
def update_subobject(
    subobject_id: int, subobject_in: schema.SubObjectBase, db: Session = Depends(get_db)
) -> schema.SubObjectResponse:
    service = SubObjectService(db)
    subobject = service.update_subobject(subobject_id, subobject_in)
    if not subobject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found")
    return schema.SubObjectResponse.model_validate(subobject)


@router.delete("/{subobject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subobject(subobject_id: int, db: Session = Depends(get_db)) -> None:
    service = SubObjectService(db)
    deleted = service.delete_subobject(subobject_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found")
