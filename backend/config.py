import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ===============================================
DEBUG_MODE = (os.getenv("DEBUG_MODE") or "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# ===============================================
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_ADMIN_NAME = os.getenv("KEYCLOAK_ADMIN_NAME")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# ===============================================
ACCESS_COOKIE = os.getenv("ACCESS_COOKIE")
REFRESH_COOKIE = os.getenv("REFRESH_COOKIE")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE")
COOKIE_SECURE = (os.getenv("COOKIE_SECURE") or "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")
