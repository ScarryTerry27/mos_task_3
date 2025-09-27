import enum
from enum import Enum
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class StatusEnum(str, Enum):
    COMPLETED = "Выполнено"
    IN_PROGRESS = "В работе"
    NOT_STARTED = "Не начато"
    ON_HOLD = "Приостановлено"


class StatusBase(BaseModel):
    status: StatusEnum
    info: Optional[str] = None


class StatusCreate(StatusBase):
    pass


class Status(StatusBase):
    status_id: int

    model_config = ConfigDict(from_attributes=True)


StatusResponse = Status


class StatusUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    info: Optional[str] = None


class CheckStatusEnum(str, Enum):
    SUCCESSFUL = "Проверка пройдена"
    INCIDENT = "Инцидент"


class RoleEnum(str, Enum):
    CONTRACTOR = "contractor"
    INSPECTOR = "inspector"
    ADMIN = "admin"


class PrescriptionTypeEnum(str, Enum):
    TYPE_1 = "Тип 1"
    TYPE_2 = "Тип 2"


class DocTypeEnum(str, Enum):
    TTN = "ТТН"
    OUTPUT = "output"


# Базовые схемы для всех моделей
class UserBase(BaseModel):
    name: str
    role: RoleEnum


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    name: str
    password: str


class PasswordResetRequest(BaseModel):
    name: str
    new_password: str


class ObjectBase(BaseModel):
    name: str
    status: StatusEnum = StatusEnum.NOT_STARTED
    address: Optional[str] = None


class ObjectCreate(ObjectBase):
    admin_id: int
    inspector_id: int
    contractor_id: int


class Object(ObjectBase):
    object_id: int
    admin_id: int
    inspector_id: int
    contractor_id: int

    model_config = ConfigDict(from_attributes=True)


ObjectResponse = Object


class SubObjectBase(BaseModel):
    name: str
    status_inspector: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    status_contractor: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    status_admin: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    prescription_info: Optional[str] = None


class SubObjectCreate(SubObjectBase):
    object_id: int


class SubObject(SubObjectBase):
    subobject_id: int
    object_id: int

    model_config = ConfigDict(from_attributes=True)


SubObjectResponse = SubObject


class CheckBase(BaseModel):
    info: Optional[str] = None
    location: Optional[str] = None
    status_check: Optional[CheckStatusEnum] = None


class CheckCreate(CheckBase):
    subobject_id: int


class Check(CheckCreate):
    check_id: int
    datetime: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentBase(BaseModel):
    photo: Optional[str] = None
    incident_status: Optional[bool] = None
    incident_info: Optional[str] = None
    prescription_type: Optional[PrescriptionTypeEnum] = None


class IncidentCreate(IncidentBase):
    check_id: int


class Incident(IncidentBase):
    incident_id: int
    check_id: int
    date: datetime


    model_config = ConfigDict(from_attributes=True)


IncidentResponse = Incident


class DocumentBase(BaseModel):
    doc_type: DocTypeEnum
    doc_number: str
    doc_date_start: date
    doc_date_end: date
    doc_image_id: str

    @field_validator("doc_type", mode="before")
    @classmethod
    def _convert_doc_type(cls, value):
        if isinstance(value, enum.Enum):
            return value.value
        return value


class DocumentCreate(DocumentBase):
    user_id: int
    object_id: int


class Document(DocumentBase):
    document_id: int
    user_id: int
    object_id: int

    model_config = ConfigDict(from_attributes=True)


class MaterialBase(BaseModel):
    name: str
    okpd: Optional[str] = None
    amount: float
    uom: str
    to_be_certified: bool
    certificate: Optional[str] = None


class MaterialCreate(MaterialBase):
    doc_id: int


class Material(MaterialBase):
    material_id: int
    doc_id: int

    model_config = ConfigDict(from_attributes=True)


# Схемы для обновления (все поля опциональны)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None


class ObjectUpdate(BaseModel):
    name: Optional[str] = None
    admin_id: Optional[int] = None
    inspector_id: Optional[int] = None
    contractor_id: Optional[int] = None
    status: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    address: Optional[str] = None


class SubObjectUpdate(BaseModel):
    name: Optional[str] = None
    status_inspector: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    status_contractor: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    status_admin: Optional[StatusEnum] = StatusEnum.NOT_STARTED
    prescription_info: Optional[str] = None
    object_id: int


class CheckUpdate(BaseModel):
    info: Optional[str] = None
    location: Optional[str] = None
    status_check: Optional[CheckStatusEnum] = None
    subobject_id: Optional[int] = None


class IncidentUpdate(BaseModel):
    photo: Optional[str] = None
    incident_status: Optional[bool] = None
    incident_info: Optional[str] = None
    prescription_type: Optional[PrescriptionTypeEnum] = None
    check_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    doc_type: Optional[DocTypeEnum] = None
    doc_number: Optional[str] = None
    doc_date_start: Optional[date] = None
    doc_date_end: Optional[date] = None
    doc_image_id: Optional[str] = None
    user_id: Optional[int] = None
    object_id: Optional[int] = None


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    okpd: Optional[str] = None
    amount: Optional[float] = None
    uom: Optional[str] = None
    to_be_certified: Optional[bool] = None
    certificate: Optional[str] = None
    doc_id: Optional[int] = None


# Простые схемы для аутентификации
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Базовая схема ответа
class MessageResponse(BaseModel):
    message: str


__all__ = [
    "StatusEnum",
    "StatusBase",
    "StatusCreate",
    "Status",
    "StatusResponse",
    "StatusUpdate",
    "CheckStatusEnum",
    "RoleEnum",
    "PrescriptionTypeEnum",
    "DocTypeEnum",
    "UserBase",
    "UserCreate",
    "User",
    "UserLogin",
    "PasswordResetRequest",
    "ObjectBase",
    "ObjectCreate",
    "Object",
    "ObjectResponse",
    "ObjectUpdate",
    "SubObjectBase",
    "SubObjectCreate",
    "SubObject",
    "SubObjectResponse",
    "SubObjectUpdate",
    "CheckBase",
    "CheckCreate",
    "Check",
    "CheckUpdate",
    "IncidentBase",
    "IncidentCreate",
    "Incident",
    "IncidentResponse",
    "IncidentUpdate",
    "DocumentBase",
    "DocumentCreate",
    "Document",
    "DocumentUpdate",
    "MaterialBase",
    "MaterialCreate",
    "Material",
    "MaterialUpdate",
    "UserUpdate",
    "LoginRequest",
    "TokenResponse",
    "MessageResponse",
]
