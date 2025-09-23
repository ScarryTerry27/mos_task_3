from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from service.db import model, schema


class UserService:
    """Service layer for CRUD operations on :class:`model.User`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_user(self, user_in: schema.UserCreate) -> model.User:
        """Create a new user in the database."""
        user = model.User(
            name=user_in.name,
            password=user_in.password,
            role=model.RoleEnum(user_in.role.value),
        )
        self._session.add(user)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise
        self._session.refresh(user)
        return user

    def list_users(self) -> List[model.User]:
        """Return all users."""
        return self._session.query(model.User).all()

    def get_user_by_id(self, user_id: int) -> Optional[model.User]:
        """Return a user by its ID."""
        return self._session.query(model.User).filter(model.User.user_id == user_id).first()

    def get_user_by_name(self, name: str) -> Optional[model.User]:
        """Return a user by its name."""
        return self._session.query(model.User).filter(model.User.name == name).first()

    def update_user(self, user_id: int, user_in: schema.UserBase) -> Optional[model.User]:
        """Update user fields."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.name = user_in.name
        user.password = user_in.password
        user.role = model.RoleEnum(user_in.role.value)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def update_password(self, user_id: int, new_password: str) -> Optional[model.User]:
        """Update password for a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.password = new_password
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by its ID."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        self._session.delete(user)
        self._session.commit()
        return True

    def authenticate(self, name: str, password: str) -> Optional[model.User]:
        """Validate user credentials."""
        user = self.get_user_by_name(name)
        if user and user.password == password:
            return user
        return None


class ObjectService:
    """Service layer for CRUD operations on :class:`model.Object`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_object(self, object_in: schema.ObjectCreate) -> model.Object:
        obj = model.Object(
            name=object_in.name,
            status=object_in.status,
            inspection_id=object_in.inspection_id,
            contractor_id=object_in.contractor_id,
        )
        self._session.add(obj)
        self._session.commit()
        self._session.refresh(obj)
        return obj

    def list_objects(self) -> List[model.Object]:
        return self._session.query(model.Object).all()

    def get_object(self, object_id: int) -> Optional[model.Object]:
        return (
            self._session.query(model.Object)
            .filter(model.Object.object_id == object_id)
            .first()
        )

    def update_object(
        self, object_id: int, object_in: schema.ObjectCreate
    ) -> Optional[model.Object]:
        obj = self.get_object(object_id)
        if not obj:
            return None

        obj.name = object_in.name
        obj.status = object_in.status
        obj.inspection_id = object_in.inspection_id
        obj.contractor_id = object_in.contractor_id
        self._session.add(obj)
        self._session.commit()
        self._session.refresh(obj)
        return obj

    def delete_object(self, object_id: int) -> bool:
        obj = self.get_object(object_id)
        if not obj:
            return False
        self._session.delete(obj)
        self._session.commit()
        return True


class SubObjectService:
    """Service layer for CRUD operations on :class:`model.SubObject`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_subobject(self, subobject_in: schema.SubObjectCreate) -> model.SubObject:
        subobject = model.SubObject(
            name=subobject_in.name,
            object_id=subobject_in.object_id,
            status_inspector=
            (
                model.StatusEnum(subobject_in.status_inspector.value)
                if subobject_in.status_inspector
                else None
            ),
            status_contractor=
            (
                model.StatusEnum(subobject_in.status_contractor.value)
                if subobject_in.status_contractor
                else None
            ),
            status_admin=
            (
                model.StatusEnum(subobject_in.status_admin.value)
                if subobject_in.status_admin
                else None
            ),
        )
        self._session.add(subobject)
        self._session.commit()
        self._session.refresh(subobject)
        return subobject

    def list_subobjects(self) -> List[model.SubObject]:
        return self._session.query(model.SubObject).all()

    def get_subobject(self, subobject_id: int) -> Optional[model.SubObject]:
        return (
            self._session.query(model.SubObject)
            .filter(model.SubObject.subobject_id == subobject_id)
            .first()
        )

    def update_subobject(
        self, subobject_id: int, subobject_in: schema.SubObjectBase
    ) -> Optional[model.SubObject]:
        subobject = self.get_subobject(subobject_id)
        if not subobject:
            return None

        subobject.name = subobject_in.name
        subobject.status_inspector = (
            model.StatusEnum(subobject_in.status_inspector.value)
            if subobject_in.status_inspector
            else None
        )
        subobject.status_contractor = (
            model.StatusEnum(subobject_in.status_contractor.value)
            if subobject_in.status_contractor
            else None
        )
        subobject.status_admin = (
            model.StatusEnum(subobject_in.status_admin.value)
            if subobject_in.status_admin
            else None
        )
        self._session.add(subobject)
        self._session.commit()
        self._session.refresh(subobject)
        return subobject

    def delete_subobject(self, subobject_id: int) -> bool:
        subobject = self.get_subobject(subobject_id)
        if not subobject:
            return False
        self._session.delete(subobject)
        self._session.commit()
        return True


class CheckService:
    """Service layer for CRUD operations on :class:`model.Check`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_check(self, check_in: schema.CheckCreate) -> model.Check:
        check = model.Check(
            subobject_id=check_in.subobject_id,
            photo=check_in.photo,
            location=check_in.location,
            info=check_in.info,
        )
        self._session.add(check)
        self._session.commit()
        self._session.refresh(check)
        return check

    def list_checks(self) -> List[model.Check]:
        return self._session.query(model.Check).all()

    def get_check(self, check_id: int) -> Optional[model.Check]:
        return (
            self._session.query(model.Check)
            .filter(model.Check.check_id == check_id)
            .first()
        )

    def update_check(
        self, check_id: int, check_in: schema.CheckBase
    ) -> Optional[model.Check]:
        check = self.get_check(check_id)
        if not check:
            return None

        check.photo = check_in.photo
        check.location = check_in.location
        check.info = check_in.info
        self._session.add(check)
        self._session.commit()
        self._session.refresh(check)
        return check

    def delete_check(self, check_id: int) -> bool:
        check = self.get_check(check_id)
        if not check:
            return False
        self._session.delete(check)
        self._session.commit()
        return True


class IncidentService:
    """Service layer for CRUD operations on :class:`model.Incident`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_incident(self, incident_in: schema.IncidentCreate) -> model.Incident:
        incident = model.Incident(
            check_id=incident_in.check_id,
            info=incident_in.info,
            photo=incident_in.photo,
        )
        self._session.add(incident)
        self._session.commit()
        self._session.refresh(incident)
        return incident

    def list_incidents(self) -> List[model.Incident]:
        return self._session.query(model.Incident).all()

    def get_incident(self, incident_id: int) -> Optional[model.Incident]:
        return (
            self._session.query(model.Incident)
            .filter(model.Incident.incident_id == incident_id)
            .first()
        )

    def update_incident(
        self, incident_id: int, incident_in: schema.IncidentBase
    ) -> Optional[model.Incident]:
        incident = self.get_incident(incident_id)
        if not incident:
            return None

        incident.info = incident_in.info
        incident.photo = incident_in.photo
        self._session.add(incident)
        self._session.commit()
        self._session.refresh(incident)
        return incident

    def delete_incident(self, incident_id: int) -> bool:
        incident = self.get_incident(incident_id)
        if not incident:
            return False
        self._session.delete(incident)
        self._session.commit()
        return True


class DocumentService:
    """Service layer for CRUD operations on :class:`model.Document`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_document(self, document_in: schema.DocumentCreate) -> model.Document:
        document = model.Document(
            check_id=document_in.check_id,
            file_id=document_in.file_id,
            doc_date=document_in.doc_date,
        )
        self._session.add(document)
        self._session.commit()
        self._session.refresh(document)
        return document

    def list_documents(self) -> List[model.Document]:
        return self._session.query(model.Document).all()

    def get_document(self, document_id: int) -> Optional[model.Document]:
        return (
            self._session.query(model.Document)
            .filter(model.Document.document_id == document_id)
            .first()
        )

    def update_document(
        self, document_id: int, document_in: schema.DocumentBase
    ) -> Optional[model.Document]:
        document = self.get_document(document_id)
        if not document:
            return None

        document.file_id = document_in.file_id
        document.doc_date = document_in.doc_date
        self._session.add(document)
        self._session.commit()
        self._session.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        document = self.get_document(document_id)
        if not document:
            return False
        self._session.delete(document)
        self._session.commit()
        return True


class MaterialService:
    """Service layer for CRUD operations on :class:`model.Material`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_material(self, material_in: schema.MaterialCreate) -> model.Material:
        material = model.Material(
            ttn_id=material_in.ttn_id,
            parsed_data=material_in.parsed_data,
        )
        self._session.add(material)
        self._session.commit()
        self._session.refresh(material)
        return material

    def list_materials(self) -> List[model.Material]:
        return self._session.query(model.Material).all()

    def get_material(self, material_id: int) -> Optional[model.Material]:
        return (
            self._session.query(model.Material)
            .filter(model.Material.material_id == material_id)
            .first()
        )

    def update_material(
        self, material_id: int, material_in: schema.MaterialBase
    ) -> Optional[model.Material]:
        material = self.get_material(material_id)
        if not material:
            return None

        material.ttn_id = material_in.ttn_id
        material.parsed_data = material_in.parsed_data
        self._session.add(material)
        self._session.commit()
        self._session.refresh(material)
        return material

    def delete_material(self, material_id: int) -> bool:
        material = self.get_material(material_id)
        if not material:
            return False
        self._session.delete(material)
        self._session.commit()
        return True


class StatusService:
    """Service layer for CRUD operations on :class:`model.Status`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_status(self, status_in: schema.StatusCreate) -> model.Status:
        status = model.Status(
            status=model.StatusEnum(status_in.status.value),
            info=status_in.info,
        )
        self._session.add(status)
        self._session.commit()
        self._session.refresh(status)
        return status

    def list_statuses(self) -> List[model.Status]:
        return self._session.query(model.Status).all()

    def get_status(self, status_id: int) -> Optional[model.Status]:
        return (
            self._session.query(model.Status)
            .filter(model.Status.status_id == status_id)
            .first()
        )

    def update_status(
        self, status_id: int, status_in: schema.StatusBase
    ) -> Optional[model.Status]:
        status = self.get_status(status_id)
        if not status:
            return None

        status.status = model.StatusEnum(status_in.status.value)
        status.info = status_in.info
        self._session.add(status)
        self._session.commit()
        self._session.refresh(status)
        return status

    def delete_status(self, status_id: int) -> bool:
        status = self.get_status(status_id)
        if not status:
            return False
        self._session.delete(status)
        self._session.commit()
        return True
