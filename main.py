from fastapi import FastAPI

from secret_santa import routes
from secret_santa.models import create_db_and_tables


app = FastAPI(
    title="Secret Santa draw generation API"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(
    routes.router,
    prefix=""
)
