from typing import Dict

from fastapi import FastAPI

from handlers.auth import router as auth_router
from service.db.db import create_tables

create_tables()

app = FastAPI(title="User Service API")
app.include_router(auth_router)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "ok"}
