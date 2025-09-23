from typing import Dict

from fastapi import FastAPI

from handlers.auth import router as auth_router
from handlers.checks import router as checks_router
from handlers.documents import router as documents_router
from handlers.incidents import router as incidents_router
from handlers.materials import router as materials_router
from handlers.objects import router as objects_router
from handlers.statuses import router as statuses_router
from handlers.subobjects import router as subobjects_router
from service.db.db import create_tables

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
