from sqlite3 import Date

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()


class StatusEnum(enum.Enum):
    COMPLETED = "Выполнено"
    IN_PROGRESS = "В работе"
    NOT_STARTED = "Не приступали"
    ON_CONTROL = "Взять на контроль"


class RoleEnum(enum.Enum):
    CONTRACTOR = "contractor"
    INSPECTOR = "inspector"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

    inspected_objects = relationship(
        "Object", back_populates="inspector", foreign_keys="Object.inspection_id"
    )
    contractor_objects = relationship(
        "Object", back_populates="contractor", foreign_keys="Object.contractor_id"
    )


class Object(Base):
    __tablename__ = "objects"

    object_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    inspection_id = Column(Integer, ForeignKey("users.user_id"))  # ID инспектора
    contractor_id = Column(Integer, ForeignKey("users.user_id"))  # ID подрядчика
    status = Column(String(50))
    address = Column(String(300))

    inspector = relationship(
        "User", back_populates="inspected_objects", foreign_keys=[inspection_id]
    )
    contractor = relationship(
        "User", back_populates="contractor_objects", foreign_keys=[contractor_id]
    )
    subobjects = relationship("SubObject", back_populates="object")


class SubObject(Base):
    __tablename__ = "subobjects"

    subobject_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    object_id = Column(Integer, ForeignKey("objects.object_id"))
    status_inspector = Column(Enum(StatusEnum))  # Статус от инспектора
    status_contractor = Column(Enum(StatusEnum))  # Статус от подрядчика (вместо prends)
    status_admin = Column(Enum(StatusEnum))  # Статус от администратора

    object = relationship("Object", back_populates="subobjects")
    checks = relationship("Check", back_populates="subobject")


class Check(Base):
    __tablename__ = "checks"

    check_id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, default=datetime.now)
    photo = Column(String(255))
    location = Column(Text)
    info = Column(Text)

    subobject_id = Column(Integer, ForeignKey("subobjects.subobject_id"))
    subobject = relationship("SubObject", back_populates="checks")
    incidents = relationship("Incident", back_populates="check")
    documents = relationship("Document", back_populates="check")


class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.utcnow)
    photo = Column(Text)
    info = Column(Text)
    check_id = Column(Integer, ForeignKey("checks.check_id"))

    check = relationship("Check", back_populates="incidents")


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(Integer, ForeignKey("checks.check_id"))
    doc_date = Column(Date)
    file_id = Column(String(100))

    check = relationship("Check", back_populates="documents")


class Material(Base):
    __tablename__ = "materials"

    material_id = Column(Integer, primary_key=True, autoincrement=True)
    ttn_id = Column(Integer)
    parsed_data = Column(Text)


class Status(Base):
    __tablename__ = "statuses"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(StatusEnum))
    info = Column(Text)
