from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.service.db import model, schema


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
