from config import (
    KEYCLOAK_SERVER_URL,
    KEYCLOAK_REALM,
    CLIENT_ID,
    CLIENT_SECRET,
    KEYCLOAK_ADMIN_NAME,
    KEYCLOAK_ADMIN_PASSWORD,
)
from services.auth import KeycloakAuthService, KeycloakAdminService


def get_auth_service() -> KeycloakAuthService:
    return KeycloakAuthService(
        server_url=KEYCLOAK_SERVER_URL,
        realm_name=KEYCLOAK_REALM,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )


def get_admin_service() -> KeycloakAdminService:
    return KeycloakAdminService(
        server_url=KEYCLOAK_SERVER_URL,
        realm_name=KEYCLOAK_REALM,
        admin_username=KEYCLOAK_ADMIN_NAME,
        admin_password=KEYCLOAK_ADMIN_PASSWORD,
    )
