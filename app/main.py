from fastapi import FastAPI

from app.config import settings
from app.routes import customers_router, health_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(customers_router)
