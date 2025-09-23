from typing import Dict

from fastapi import FastAPI

from backend.handlers.auth import router as auth_router
from backend.handlers.checks import router as checks_router
from backend.handlers.documents import router as documents_router
from backend.handlers.incidents import router as incidents_router
from backend.handlers.materials import router as materials_router
from backend.handlers.objects import router as objects_router
from backend.handlers.statuses import router as statuses_router
from backend.handlers.subobjects import router as subobjects_router
from backend.service.db.db import create_tables

create_tables()

app = FastAPI(title="User Service API")
app.include_router(auth_router)
app.include_router(objects_router)
app.include_router(subobjects_router)
app.include_router(checks_router)
app.include_router(incidents_router)
app.include_router(documents_router)
app.include_router(materials_router)
app.include_router(statuses_router)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "ok"}
