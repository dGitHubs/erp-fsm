from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import (
    customers_router,
    health_router,
    manufacturing_orders_router,
    materials_router,
    product_materials_router,
    products_router,
)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(customers_router)
app.include_router(manufacturing_orders_router)
app.include_router(materials_router)
app.include_router(product_materials_router)
app.include_router(products_router)