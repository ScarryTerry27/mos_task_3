from typing import Dict

from fastapi import FastAPI, Depends

from handlers.auth import k_auth_router, router as auth_router
from handlers.checks import router as checks_router
from handlers.documents import router as documents_router
from handlers.incidents import router as incidents_router
from handlers.materials import router as materials_router
from handlers.objects import router as objects_router
from handlers.subobjects import router as subobjects_router
from services.db.db import create_tables

from security import get_current_user

create_tables()

app = FastAPI(title="User Service API")
app.include_router(auth_router)
app.include_router(k_auth_router)

protected = [Depends(get_current_user)]
app.include_router(objects_router, dependencies=protected)
app.include_router(subobjects_router, dependencies=protected)
app.include_router(checks_router, dependencies=protected)
app.include_router(incidents_router, dependencies=protected)
app.include_router(documents_router, dependencies=protected)
app.include_router(materials_router, dependencies=protected)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "ok"}
