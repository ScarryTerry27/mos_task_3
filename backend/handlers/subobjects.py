from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.db import schema
from service.db.db import get_db
from service.db.service import SubObjectService

router = APIRouter(prefix="/subobjects", tags=["subobjects"])


@router.post("/", response_model=schema.SubObject, status_code=status.HTTP_201_CREATED)
def create_subobject(
    subobject_in: schema.SubObjectCreate, db: Session = Depends(get_db)
) -> schema.SubObject:
    # может создать только админ, если кто то другой - недостаточность прав
    # нужно проверить существует ли object_id - если нет - возвращаем нот фоунд
    service = SubObjectService(db)
    subobject = service.create_subobject(subobject_in)
    return schema.SubObject.model_validate(subobject)


@router.get("/", response_model=List[schema.SubObject])
def list_subobjects(db: Session = Depends(get_db)) -> List[schema.SubObject]:
    # Ситуация как в объекте - возвращем админу все с оффсетом и лимитом, остальным только их проекты
    service = SubObjectService(db)
    subobjects = service.list_subobjects()
    return [schema.SubObject.model_validate(item) for item in subobjects]


@router.get("/{subobject_id}", response_model=schema.SubObject)
def get_subobject(subobject_id: int, db: Session = Depends(get_db)) -> schema.SubObject:
    # так же как в объекте
    service = SubObjectService(db)
    subobject = service.get_subobject(subobject_id)
    if not subobject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found")
    return schema.SubObject.model_validate(subobject)


@router.put("/{subobject_id}", response_model=schema.SubObject)
def update_subobject(
    subobject_id: int, subobject_in: schema.SubObjectUpdate, db: Session = Depends(get_db)
) -> schema.SubObject:
    # так же как в объекте - только апдейтить может еще instructor - свое поле статус инструктор -
    # статус админ если мелькает от инспектора - возвращаем отсутствие прав
    # апдейтить может и конструктор - только свой статус, если он пытается обновить статус у других ролей - возвращаем
    # недостаточность прав
    service = SubObjectService(db)
    subobject = service.update_subobject(subobject_id, subobject_in)
    if not subobject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found")
    return schema.SubObject.model_validate(subobject)


@router.delete("/{subobject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subobject(subobject_id: int, db: Session = Depends(get_db)) -> None:
    # так же как в объекте - удалять может только админ
    service = SubObjectService(db)
    deleted = service.delete_subobject(subobject_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found")

