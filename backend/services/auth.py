from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakGetError


class KeycloakAuthService:
    def __init__(
        self, server_url: str, realm_name: str, client_id: str, client_secret: str
    ):
        self.server_url = server_url
        self.realm = realm_name
        self.client_id = client_id
        self.client_secret = client_secret
        self._oidc = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret,
        )

    def format_username(self, name: str) -> str:
        return f"{name}_{self.client_id}"

    def token_password(self, username: str, password: str) -> dict:
        return self._oidc.token(
            grant_type="password", username=username, password=password
        )

    def refresh(self, refresh_token: str) -> dict:
        return self._oidc.refresh_token(refresh_token)


class KeycloakAdminService:
    def __init__(
        self, server_url: str, realm_name: str, admin_username: str, admin_password: str
    ):
        self.server_url = server_url
        self.realm = realm_name
        self.admin = KeycloakAdmin(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name=realm_name,
            user_realm_name="master",
            verify=True,
        )

    def get_user_id_by_username(self, username: str) -> str | None:
        uid = self.admin.get_user_id(username)
        return uid

    def get_or_create_user(
        self, username: str, password: str, enabled: bool = True
    ) -> str:
        uid = self.get_user_id_by_username(username)
        if uid:
            return uid
        try:
            return self.create_user(username, password, enabled)
        except KeycloakGetError:
            uid = self.get_user_id_by_username(username)
            if uid:
                return uid
            raise

    def create_user(self, username: str, password: str, enabled: bool = True) -> str:
        payload = {
            "username": username,
            "enabled": enabled,
            "credentials": [
                {"value": password, "type": "password", "temporary": False}
            ],
        }
        return self.admin.create_user(payload)

    def set_user_password(
        self, user_id: str, new_password: str, temporary: bool = False
    ) -> None:
        self.admin.set_user_password(
            user_id=user_id, password=new_password, temporary=temporary
        )

    def ensure_realm_roles(self, role_names: list[str]) -> None:
        existing = {role["name"] for role in self.admin.get_realm_roles()}
        for name in role_names:
            if name not in existing:
                self.admin.create_realm_role({"name": name})

    def assign_realm_roles(self, user_id: str, role_names: list[str]) -> None:
        roles = []
        all_roles = self.admin.get_realm_roles()
        by_name = {r["name"]: r for r in all_roles}
        for name in role_names:
            role = by_name.get(name)
            if role:
                roles.append({"id": role["id"], "name": role["name"]})
        if roles:
            self.admin.assign_realm_roles(user_id=user_id, roles=roles)

    def ensure_group(self, group_name: str) -> str:
        for group in self.admin.get_groups():
            if group["name"] == group_name:
                return group["id"]
        group_id = self.admin.create_group({"name": group_name})
        return group_id

    def add_user_to_group(self, user_id: str, group_id: str) -> None:
        self.admin.group_user_add(user_id=user_id, group_id=group_id)

    def set_user_attributes(self, user_id: str, attrs: dict[str, str]) -> None:
        user = self.admin.get_user(user_id)
        user["attributes"] = user.get("attributes", {}) or {}
        for key, value in attrs.items():
            user["attributes"][key] = [str(value)]
        self.admin.update_user(user_id, user)
