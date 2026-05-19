from app.routes.customers import router as customers_router
from app.routes.health import router as health_router
from app.routes.manufacturing_orders import router as manufacturing_orders_router
from app.routes.materials import router as materials_router
from app.routes.product_materials import router as product_materials_router
from app.routes.products import router as products_router

__all__ = [
    "health_router",
    "customers_router",
    "manufacturing_orders_router",
    "materials_router",
    "product_materials_router",
    "products_router",
]