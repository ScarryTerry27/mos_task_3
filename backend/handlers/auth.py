from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.service.db import schema
from backend.service.db.db import get_db
from backend.service.db.service import UserService
from backend.service.keycloak import KeycloakService, get_keycloak_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schema.User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schema.UserCreate,
    db: Session = Depends(get_db),
    keycloak_service: KeycloakService = Depends(get_keycloak_service),
) -> schema.User:
    service = UserService(db)

    existing_user = service.get_user_by_name(user_in.name)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    keycloak_service.create_user(user_in.name, user_in.password, user_in.role.value)

    try:
        user = service.create_user(user_in)
    except IntegrityError as exc:
        keycloak_service.delete_user(user_in.name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create user in the database",
        ) from exc
    return schema.User.model_validate(user)


@router.post("/login", response_model=schema.User)
def login_user(
    credentials: schema.UserLogin,
    response: Response,
    db: Session = Depends(get_db),
    keycloak_service: KeycloakService = Depends(get_keycloak_service),
) -> schema.User:
    service = UserService(db)

    user = service.authenticate(credentials.name, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    tokens = keycloak_service.issue_user_tokens(credentials.name, credentials.password)
    keycloak_service.set_token_cookies(response, tokens)

    return schema.User.model_validate(user)


@router.post("/forgot-password", response_model=schema.User)
def forgot_password(
    payload: schema.PasswordResetRequest,
    db: Session = Depends(get_db),
    keycloak_service: KeycloakService = Depends(get_keycloak_service),
) -> schema.User:
    service = UserService(db)

    user = service.get_user_by_name(payload.name)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    keycloak_service.reset_password(payload.name, payload.new_password)

    updated_user = service.update_password(user.user_id, payload.new_password)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to update password")

    return schema.User.model_validate(updated_user)
