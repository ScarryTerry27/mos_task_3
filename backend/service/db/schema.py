from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class StatusEnum(str, Enum):
    COMPLETED = "Выполнено"
    IN_PROGRESS = "В работе"
    NOT_STARTED = "Не приступали"
    ON_CONTROL = "Взять на контроль"


class RoleEnum(str, Enum):
    CONTRACTOR = "contractor"
    INSPECTOR = "inspector"
    ADMIN = "admin"


class UserBase(BaseModel):
    name: str
    password: str
    role: RoleEnum


class UserCreate(UserBase):
    pass


class User(UserBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ObjectBase(BaseModel):
    name: str
    status: Optional[str] = None


class ObjectCreate(ObjectBase):
    inspection_id: Optional[int] = None
    contractor_id: Optional[int] = None


class Object(ObjectBase):
    object_id: int
    inspection_id: Optional[int]
    contractor_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class SubObjectBase(BaseModel):
    name: str
    status_inspector: Optional[StatusEnum] = None
    status_contractor: Optional[StatusEnum] = None
    status_admin: Optional[StatusEnum] = None


class SubObjectCreate(SubObjectBase):
    object_id: int


class SubObject(SubObjectBase):
    subobject_id: int
    object_id: int

    model_config = ConfigDict(from_attributes=True)


class CheckBase(BaseModel):
    phone: Optional[str] = None
    photo: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    info: Optional[str] = None


class CheckCreate(CheckBase):
    subobject_id: int


class Check(CheckBase):
    check_id: int
    datetime: datetime
    subobject_id: int

    model_config = ConfigDict(from_attributes=True)


class IncidentBase(BaseModel):
    info: str


class IncidentCreate(IncidentBase):
    check_id: int


class Incident(IncidentBase):
    incident_id: int
    date: datetime
    check_id: int

    model_config = ConfigDict(from_attributes=True)


class DocumentBase(BaseModel):
    file_id: str


class DocumentCreate(DocumentBase):
    check_id: int


class Document(DocumentBase):
    document_id: int
    date: datetime
    check_id: int

    model_config = ConfigDict(from_attributes=True)


class MaterialBase(BaseModel):
    tm_id: Optional[int] = None
    parsed_data: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class Material(MaterialBase):
    material_id: int

    model_config = ConfigDict(from_attributes=True)


class StatusBase(BaseModel):
    status: StatusEnum
    info: Optional[str] = None


class StatusCreate(StatusBase):
    pass


class Status(StatusBase):
    status_id: int

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    name: str
    password: str


class PasswordResetRequest(BaseModel):
    name: str
    new_password: str

