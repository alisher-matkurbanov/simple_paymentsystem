import logging

from fastapi import FastAPI

from app.database import db
from app.api import router

logger = logging.getLogger(__name__)

# Шутка дня
# https://twitter.com/nikmostovoy/status/1403740216893095940

app = FastAPI()


@app.on_event("startup")
async def startup():
    if not db.is_connected:
        await db.connect()


@app.on_event("shutdown")
async def shutdown():
    if db.is_connected:
        await db.disconnect()


app.include_router(router)
