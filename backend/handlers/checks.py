from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from security import get_current_user
from services.db import schema
from services.db.db import get_db
from services.db.service import (
    CheckService,
    IncidentService,
    ObjectService,
    SubObjectService,
)
from services.others.video_client import analyze_video

router = APIRouter(prefix="/checks", tags=["checks"])


def _ensure_subobject_access(
    db: Session, subobject_id: int, current_user: schema.User
) -> None:
    subobject_service = SubObjectService(db)
    subobject = subobject_service.get_subobject(subobject_id)
    if not subobject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subobject not found"
        )

    if current_user.role == schema.RoleEnum.INSPECTOR:
        object_service = ObjectService(db)
        parent_object = object_service.get_object(subobject.object_id)
        if not parent_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Object not found"
            )
        if parent_object.inspector_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )


@router.post("/", response_model=schema.Check, status_code=status.HTTP_201_CREATED)
def create_check(
    check_in: schema.CheckCreate, db: Session = Depends(get_db)
) -> schema.Check:
    # только админы и instructor юзерам не видно
    # так же реализовать проверки обзяательных полей
    # реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    current_user = get_current_user()
    if current_user.role not in (schema.RoleEnum.ADMIN, schema.RoleEnum.INSPECTOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    _ensure_subobject_access(db, check_in.subobject_id, current_user)

    service = CheckService(db)
    check = service.create_check(check_in)
    return schema.Check.model_validate(check)


@router.get("/", response_model=List[schema.Check])
def list_checks(db: Session = Depends(get_db)) -> List[schema.Check]:
    # только не юзерам - при этом показываем админу все проверки, а instructor его проверки
    # так же реализовать проверку полей и id
    # реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    current_user = get_current_user()
    if current_user.role not in (schema.RoleEnum.ADMIN, schema.RoleEnum.INSPECTOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    service = CheckService(db)
    checks = service.list_checks(role=current_user.role, user_id=current_user.user_id)
    return [schema.Check.model_validate(item) for item in checks]


@router.get("/{check_id}", response_model=schema.Check)
def get_check(check_id: int, db: Session = Depends(get_db)) -> schema.Check:
    # только не юзерам
    # реализовать проверку обязательных полей
    # реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    current_user = get_current_user()
    if current_user.role not in (schema.RoleEnum.ADMIN, schema.RoleEnum.INSPECTOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    service = CheckService(db)
    check = service.get_check(check_id)
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Check not found"
        )
    _ensure_subobject_access(db, check.subobject_id, current_user)
    return schema.Check.model_validate(check)


@router.put("/{check_id}", response_model=schema.Check)
def update_check(
    check_id: int, check_in: schema.CheckUpdate, db: Session = Depends(get_db)
) -> schema.Check:
    # только не юзерам так же реализовать проверку что instructor имеет доступ к данной проверке и субобъекту
    current_user = get_current_user()
    if current_user.role not in (schema.RoleEnum.ADMIN, schema.RoleEnum.INSPECTOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    service = CheckService(db)
    existing_check = service.get_check(check_id)
    if not existing_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Check not found"
        )
    _ensure_subobject_access(db, existing_check.subobject_id, current_user)

    if "subobject_id" in check_in.model_fields_set:
        _ensure_subobject_access(db, check_in.subobject_id, current_user)

    check = service.update_check(check_id, check_in)
    return schema.Check.model_validate(check)


@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_check(check_id: int, db: Session = Depends(get_db)) -> None:
    # только админ
    current_user = get_current_user()
    if current_user.role is not schema.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    service = CheckService(db)
    deleted = service.delete_check(check_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Check not found"
        )


@router.post(
    "/process-video",
    response_model=schema.VideoProcessingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_video(
    subobject_id: int = Form(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> schema.VideoProcessingResponse:
    """Accept a video, forward it to the analysis service and persist results."""

    current_user = get_current_user()
    if current_user.role is not schema.RoleEnum.INSPECTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only inspectors are allowed to process videos",
        )

    if subobject_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="subobject_id must be a positive integer",
        )

    if video.content_type not in {"video/mp4", "video/mpeg", "video/quicktime"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only MP4, MPEG and QuickTime are allowed.",
        )

    _ensure_subobject_access(db, subobject_id, current_user)

    video_bytes = await video.read()
    check_data, incidents_data = analyze_video(video_bytes)

    check_create = schema.CheckCreate(
        subobject_id=subobject_id,
        info=check_data.info,
        location=check_data.location,
        status_check=check_data.status_check,
    )

    check_service = CheckService(db)
    incident_service = IncidentService(db)

    created_check = check_service.create_check(check_create)
    saved_incidents: list[schema.Incident] = []
    for incident_data in incidents_data:
        incident_create = schema.IncidentCreate(
            check_id=created_check.check_id,
            photo=incident_data.photo,
            incident_status=incident_data.incident_status,
            incident_info=incident_data.incident_info,
            prescription_type=incident_data.prescription_type,
        )
        incident = incident_service.create_incident(incident_create)
        saved_incidents.append(schema.Incident.model_validate(incident))

    response = schema.VideoProcessingResponse(
        check=schema.Check.model_validate(created_check),
        incidents=saved_incidents,
    )

    return response
