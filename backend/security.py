from fastapi import HTTPException, Request, Depends
from jose import jwt
from pydantic import BaseModel, Field
from typing import Set
import requests
from services.db.schema import RoleEnum

from config import (
    ACCESS_COOKIE,
    KEYCLOAK_SERVER_URL,
    KEYCLOAK_REALM,
)


class TokenPayload(BaseModel):
    user_id: str
    project_name: str
    roles: Set[RoleEnum] = Field(default_factory=set)
    company: str | None = None


def _extract_roles(claims: dict, userinfo: dict) -> Set[RoleEnum]:
    """
    Берём роли из realm_access.roles и resource_access, маппим в RoleEnum, лишние игнорим
    """
    found: set[str] = set()

    realm_access = userinfo.get("realm_access") or claims.get("realm_access") or {}
    roles = realm_access.get("roles") or []
    found.update(r for r in roles if isinstance(r, str))

    resource_access = (
        userinfo.get("resource_access") or claims.get("resource_access") or {}
    )
    for client_data in resource_access.values():
        r = client_data.get("roles") or []
        found.update(x for x in r if isinstance(x, str))

    mapped: Set[RoleEnum] = set()
    for r in found:
        upper = r.strip().upper()
        if upper in RoleEnum.__members__:
            mapped.add(RoleEnum[upper])
    return mapped


def _extract_company(userinfo: dict) -> str | None:
    """
    Берем company из групп или атрибутов
    """
    groups = userinfo.get("groups")
    if isinstance(groups, list) and groups:
        g = groups[0]
        if isinstance(g, str):
            return g.split("/")[-1] or None

    company = userinfo.get("company")
    if isinstance(company, str):
        return company

    attrs = userinfo.get("attributes") or {}
    comp_list = attrs.get("company")
    if isinstance(comp_list, list) and comp_list:
        return str(comp_list[0])

    return None


def get_current_user(request: Request) -> TokenPayload:
    """
    Валидируем токен и получаем из него даные
    """
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует токен")

    try:
        claims = jwt.get_unverified_claims(token)
        issuer = claims.get("iss") or f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"
        userinfo_url = f"{issuer.rstrip('/')}/protocol/openid-connect/userinfo"
    except Exception:
        raise HTTPException(status_code=401, detail="Невалидный или истекший токен")

    try:
        resp = requests.get(
            userinfo_url, headers={"Authorization": f"Bearer {token}"}, timeout=3
        )
    except Exception:
        raise HTTPException(status_code=503, detail="Ошибка аутентификации")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=401 if resp.status_code in (401, 403) else 503,
            detail="Невалидный или истекший токен"
            if resp.status_code in (401, 403)
            else "Ошибка аутентификации",
        )

    try:
        userinfo = resp.json()
        user_id = userinfo.get("sub")
        if not user_id:
            raise ValueError

        project_name = claims.get("azp") or claims.get("aud")
        if isinstance(project_name, list):
            project_name = project_name[0]
        if not project_name:
            raise ValueError

        roles = _extract_roles(claims, userinfo)
        company = _extract_company(userinfo)
    except Exception:
        raise HTTPException(status_code=401, detail="Невалидный или истекший токен")

    return TokenPayload(
        user_id=user_id,
        project_name=project_name,
        roles=roles,
        company=company,
    )


def require_roles(*required: RoleEnum):
    """
    Полезный вещь, можем сразу через зависимости отрубать ручки по ролям
    """

    def _dep(payload: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not required or payload.roles.intersection(required):
            return payload
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return _dep
