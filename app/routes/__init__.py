from app.routes.customers import router as customers_router
from app.routes.health import router as health_router

__all__ = ["health_router", "customers_router"]
