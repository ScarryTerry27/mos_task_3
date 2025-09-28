from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from services.db import schema
from services.db.db import get_db
from services.db.service import UserService


from config import (
    ACCESS_COOKIE,
    REFRESH_COOKIE,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    COOKIE_DOMAIN,
)

from dependencies import get_auth_service
from services.auth import KeycloakAuthService
from services.db.schema import User as UserSchema, UserCreate, UserLogin, RoleEnum


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=schema.User, status_code=status.HTTP_201_CREATED
)
def register_user(
    user_in: schema.UserCreate, db: Session = Depends(get_db)
) -> schema.User:
    service = UserService(db)

    existing_user = service.get_user_by_name(user_in.name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    user = service.create_user(user_in)
    return schema.User.model_validate(user)


@router.post("/login", response_model=schema.User)
def login_user(
    credentials: schema.UserLogin, db: Session = Depends(get_db)
) -> schema.User:
    service = UserService(db)

    user = service.authenticate(credentials.name, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return schema.User.model_validate(user)


@router.post("/forgot-password", response_model=schema.User)
def forgot_password(
    payload: schema.PasswordResetRequest, db: Session = Depends(get_db)
) -> schema.User:
    service = UserService(db)

    user = service.get_user_by_name(payload.name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    updated_user = service.update_password(user.user_id, payload.new_password)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update password",
        )

    return schema.User.model_validate(updated_user)


k_auth_router = APIRouter(prefix="/keycloak_auth", tags=["KeycloakAuthorisation"])
DEFAULT_ROLE = RoleEnum.CONTRACTOR


def _set_auth_cookies(response: Response, tokens: dict) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=tokens["access_token"],
        httponly=True,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        domain=COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=tokens["refresh_token"],
        httponly=True,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        domain=COOKIE_DOMAIN,
        path="/",
    )


@k_auth_router.post("/login", response_model=UserSchema)
def key_login_user(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
    auth: KeycloakAuthService = Depends(get_auth_service),
) -> UserSchema:
    kc_username = auth.format_username(credentials.name)
    try:
        tokens = auth.token_password(kc_username, credentials.password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидные данные"
        )

    _set_auth_cookies(response, tokens)

    users = UserService(db)
    user = users.get_user_by_name(credentials.name)
    if not user:
        user = users.create_user(
            UserCreate(
                name=credentials.name,
                password="*",
                role=DEFAULT_ROLE,
            )
        )
    return UserSchema.model_validate(user)


@k_auth_router.post("/refresh", status_code=204)
def refresh_tokens(
    request: Request,
    response: Response,
    auth: KeycloakAuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Отсутствует refresh token")
    try:
        tokens = auth.refresh(refresh_token)
    except Exception:
        # временно, чтобы понять причину
        import logging

        logging.getLogger("auth").exception("Refresh failed")
        # Сбросим испорченные куки, чтобы фронт ушёл на /login
        response.delete_cookie(ACCESS_COOKIE, path="/", domain=COOKIE_DOMAIN)
        response.delete_cookie(REFRESH_COOKIE, path="/", domain=COOKIE_DOMAIN)
        raise HTTPException(status_code=401, detail="Невалидный refresh token")

    _set_auth_cookies(response, tokens)
    return Response(status_code=204)


@k_auth_router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(ACCESS_COOKIE, path="/", domain=COOKIE_DOMAIN)
    response.delete_cookie(REFRESH_COOKIE, path="/", domain=COOKIE_DOMAIN)
    return Response(status_code=204)
