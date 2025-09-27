from service.db import schema


def get_current_user() -> schema.User:
    """Return the current authenticated user.

    This is a temporary stub that always returns an admin user. It should be
    replaced with real authentication that extracts the user information from
    Keycloak tokens.
    """

    return schema.User(user_id=1, name="Admin", role=schema.RoleEnum.ADMIN)
