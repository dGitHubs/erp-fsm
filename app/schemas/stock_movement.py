from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.stock_movement import MovementType


class StockMovementResponse(BaseModel):
    id: int
    material_id: int
    quantity: float
    movement_type: MovementType
    reference: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)