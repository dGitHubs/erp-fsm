from pydantic import BaseModel


class ManufacturingOrderMaterialAvailabilityLineResponse(BaseModel):
    material_id: int
    required_quantity: float
    available_quantity: float
    missing_quantity: float


class ManufacturingOrderMaterialAvailabilityResponse(BaseModel):
    manufacturing_order_id: int
    product_id: int
    order_quantity: int
    can_produce: bool
    lines: list[ManufacturingOrderMaterialAvailabilityLineResponse]