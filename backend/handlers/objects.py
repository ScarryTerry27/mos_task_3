from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.db import schema
from service.db.db import get_db
from service.db.service import ObjectService

router = APIRouter(prefix="/objects", tags=["objects"])


@router.post("/", response_model=schema.Object, status_code=status.HTTP_201_CREATED)
def create_object(
    object_in: schema.ObjectCreate, db: Session = Depends(get_db)
) -> schema.Object:
    # здесь считываем роль пользователя и если она не админ - то не даем создавать объекты - возвращаем ошибку на
    # недостаточность прав
    # так же нужно выполнить проверку всех id в объекте - если данного id не существует - то так же возвращаем ощибку
    # not found на id
    service = ObjectService(db)
    obj = service.create_object(object_in)
    return schema.Object.model_validate(obj)


@router.get("/", response_model=List[schema.Object])
def list_objects(db: Session = Depends(get_db)) -> List[schema.Object]:
    # тут мы должны проверить роль пользователя - если он админ то возвращаем все объекты, если нет - то только объекты,
    # связанные с ним
    # так же добавить оффсет и лимит и считывать изначально из бд по офсеты и лимиту, чтобы не переполнять память
    service = ObjectService(db)
    objects = service.list_objects()
    return [schema.Object.model_validate(obj) for obj in objects]


@router.get("/{object_id}", response_model=schema.Object)
def get_object(object_id: int, db: Session = Depends(get_db)) -> schema.Object:
    #  здесь так же реализовать проверку если админ - любой объект можно вернуть, если нет - то только объекты,
    #  привязанные к тебе
    # если ты стучишься не будучи админом к объекты, который тебе недоступен - возвращаем нет прав и соот ошибку
    service = ObjectService(db)
    obj = service.get_object(object_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return schema.Object.model_validate(obj)


@router.put("/{object_id}", response_model=schema.Object)
def update_object(
    object_id: int, object_in: schema.ObjectUpdate, db: Session = Depends(get_db)
) -> schema.Object:
    # изменять могут только админы, если стучиться не админ - отправляем ему недостаточность прав

    service = ObjectService(db)
    obj = service.update_object(object_id, object_in)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return schema.Object.model_validate(obj)


@router.delete("/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_object(object_id: int, db: Session = Depends(get_db)) -> None:
    # удалять могут только админы, если стучиться не админ - отправляем ему недостаточность прав
    service = ObjectService(db)
    deleted = service.delete_object(object_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")

