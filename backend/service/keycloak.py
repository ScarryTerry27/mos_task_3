from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException, Response, status

import config


class KeycloakService:
    """Utility class for interacting with Keycloak."""

    def __init__(self) -> None:
        self._server_url = config.KEYCLOAK_SERVER_URL.rstrip("/")
        self._realm = config.KEYCLOAK_REALM
        self._client_id = config.KEYCLOAK_CLIENT_ID
        self._client_secret = config.KEYCLOAK_CLIENT_SECRET
        self._admin_username = config.KEYCLOAK_ADMIN
        self._admin_password = config.KEYCLOAK_ADMIN_PASSWORD
        self._admin_client_id = config.KEYCLOAK_ADMIN_CLIENT_ID
        self._admin_client_secret = config.KEYCLOAK_ADMIN_CLIENT_SECRET
        self._admin_realm = config.KEYCLOAK_ADMIN_REALM
        self._cookie_secure = config.KEYCLOAK_COOKIE_SECURE
        self._cookie_samesite = config.KEYCLOAK_COOKIE_SAMESITE
        self._cookie_domain = config.KEYCLOAK_COOKIE_DOMAIN

    def issue_user_tokens(self, username: str, password: str) -> Dict[str, Any]:
        """Return token payload for a user."""
        data: Dict[str, Any] = {
            "grant_type": "password",
            "client_id": self._client_id,
            "username": username,
            "password": password,
        }
        if self._client_secret:
            data["client_secret"] = self._client_secret

        response = self._post_form(self._token_url(self._realm), data)
        if response.status_code != status.HTTP_200_OK:
            detail = self._safe_error_message(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail or "Failed to obtain tokens from Keycloak",
            )

        payload = response.json()
        if "access_token" not in payload:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Keycloak response did not contain an access token",
            )
        return payload

    def set_token_cookies(self, response: Response, tokens: Dict[str, Any]) -> None:
        """Store access and refresh tokens in HTTP-only cookies."""
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")
        refresh_expires_in = tokens.get("refresh_expires_in")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to read access token",
            )

        response.set_cookie(
            key=config.KEYCLOAK_ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=self._cookie_secure,
            samesite=self._cookie_samesite,
            max_age=expires_in,
            domain=self._cookie_domain,
            path="/",
        )

        if refresh_token:
            response.set_cookie(
                key=config.KEYCLOAK_REFRESH_COOKIE_NAME,
                value=refresh_token,
                httponly=True,
                secure=self._cookie_secure,
                samesite=self._cookie_samesite,
                max_age=refresh_expires_in,
                domain=self._cookie_domain,
                path="/",
            )

    def create_user(self, username: str, password: str, role: Optional[str] = None) -> None:
        """Create a user within the configured Keycloak realm."""
        admin_token = self._get_admin_access_token()
        headers = self._authorization_headers(admin_token)

        payload: Dict[str, Any] = {
            "username": username,
            "enabled": True,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }
            ],
        }
        if role:
            payload["attributes"] = {"role": [role]}

        response = self._request(
            method="post",
            url=self._users_url(),
            headers=headers,
            json=payload,
        )

        if response.status_code == status.HTTP_201_CREATED:
            return
        if response.status_code == status.HTTP_409_CONFLICT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists in Keycloak",
            )

        detail = self._safe_error_message(response)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail or "Failed to create user in Keycloak",
        )

    def reset_password(self, username: str, new_password: str) -> None:
        """Synchronise a password change with Keycloak."""
        admin_token = self._get_admin_access_token()
        user_id = self._get_user_id(username, admin_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in Keycloak",
            )

        payload = {
            "type": "password",
            "value": new_password,
            "temporary": False,
        }

        response = self._request(
            method="put",
            url=f"{self._users_url()}/{user_id}/reset-password",
            headers=self._authorization_headers(admin_token),
            json=payload,
        )

        if response.status_code not in (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK):
            detail = self._safe_error_message(response)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=detail or "Failed to update password in Keycloak",
            )

    def delete_user(self, username: str) -> None:
        """Remove a user from Keycloak if they exist."""
        admin_token = self._get_admin_access_token()
        user_id = self._get_user_id(username, admin_token)
        if not user_id:
            return

        self._request(
            method="delete",
            url=f"{self._users_url()}/{user_id}",
            headers=self._authorization_headers(admin_token),
        )

    def _get_admin_access_token(self) -> str:
        data: Dict[str, Any] = {
            "grant_type": "password",
            "client_id": self._admin_client_id,
            "username": self._admin_username,
            "password": self._admin_password,
        }
        if self._admin_client_secret:
            data["client_secret"] = self._admin_client_secret

        response = self._post_form(self._token_url(self._admin_realm), data)
        if response.status_code != status.HTTP_200_OK:
            detail = self._safe_error_message(response)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=detail or "Unable to authenticate against Keycloak admin API",
            )

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Keycloak admin token response missing access token",
            )
        return access_token

    def _get_user_id(self, username: str, access_token: str) -> Optional[str]:
        response = self._request(
            method="get",
            url=self._users_url(),
            headers=self._authorization_headers(access_token),
            params={"username": username},
        )

        if response.status_code != status.HTTP_200_OK:
            detail = self._safe_error_message(response)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=detail or "Failed to query Keycloak users",
            )

        for user in response.json():
            if user.get("username", "").lower() == username.lower():
                return user.get("id")
        return None

    def _authorization_headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _token_url(self, realm: str) -> str:
        return f"{self._server_url}/realms/{realm}/protocol/openid-connect/token"

    def _users_url(self) -> str:
        return f"{self._server_url}/admin/realms/{self._realm}/users"

    def _post_form(self, url: str, data: Dict[str, Any]) -> requests.Response:
        return self._request(
            method="post",
            url=url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
        except requests.RequestException as exc:  # pragma: no cover - network failure handling
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to communicate with Keycloak",
            ) from exc
        return response

    def _safe_error_message(self, response: requests.Response) -> Optional[str]:
        try:
            payload = response.json()
        except ValueError:
            return response.text if response.text else None
        if isinstance(payload, dict):
            return payload.get("error_description") or payload.get("error") or payload.get("message")
        return None


def get_keycloak_service() -> KeycloakService:
    return KeycloakService()
