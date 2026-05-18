from fastapi import FastAPI

from app.routes import health

app = FastAPI(title="ERP-FSM")

app.include_router(health.router)
