from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ManufacturingOrderStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class ManufacturingOrderCreate(BaseModel):
    reference: str
    customer_id: int
    product_id: int
    quantity: int = Field(gt=0)
    description: str | None = None
    status: ManufacturingOrderStatus = ManufacturingOrderStatus.DRAFT


class ManufacturingOrderResponse(BaseModel):
    id: int
    reference: str
    customer_id: int
    product_id: int
    quantity: int
    description: str | None
    status: ManufacturingOrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)