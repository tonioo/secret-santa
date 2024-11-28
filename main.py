from contextlib import asynccontextmanager

from fastapi import FastAPI

from secret_santa import routes
from secret_santa.models import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Secret Santa draw generation API",
    lifespan=lifespan
)

app.include_router(
    routes.router,
    prefix=""
)
