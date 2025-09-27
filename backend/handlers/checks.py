from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from services.db import schema
from services.db.db import get_db
from services.db.service import CheckService

router = APIRouter(prefix="/checks", tags=["checks"])


@router.post("/", response_model=schema.Check, status_code=status.HTTP_201_CREATED)
def create_check(
    check_in: schema.CheckCreate, db: Session = Depends(get_db)
) -> schema.Check:
    # только админы и instructor юзерам не видно
    # так же реализовать проверки обзяательных полей
    # реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    service = CheckService(db)
    check = service.create_check(check_in)
    return schema.Check.model_validate(check)


@router.get("/", response_model=List[schema.Check])
def list_checks(db: Session = Depends(get_db)) -> List[schema.Check]:
    # только не юзерам - при этом показываем админу все проверки, а instructor его проверки
    # так же реализовать проверку полей и id
    # реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    service = CheckService(db)
    checks = service.list_checks()
    return [schema.Check.model_validate(item) for item in checks]


@router.get("/{check_id}", response_model=schema.Check)
def get_check(check_id: int, db: Session = Depends(get_db)) -> schema.Check:
    # только не юзерам
    # реализовать проверку обязательных полей
    # реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    service = CheckService(db)
    check = service.get_check(check_id)
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")
    return schema.Check.model_validate(check)


@router.put("/{check_id}", response_model=schema.Check)
def update_check(
    check_id: int, check_in: schema.CheckUpdate, db: Session = Depends(get_db)
) -> schema.Check:
    # только не юзерам так же реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    service = CheckService(db)
    check = service.update_check(check_id, check_in)
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")
    return schema.Check.model_validate(check)


@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_check(check_id: int, db: Session = Depends(get_db)) -> None:
    # только админ
    service = CheckService(db)
    deleted = service.delete_check(check_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")

