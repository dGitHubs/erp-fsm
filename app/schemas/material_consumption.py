from pydantic import BaseModel


class MaterialConsumptionLineResponse(BaseModel):
    material_id: int
    quantity_consumed: float
    quantity_on_hand_before: float
    quantity_on_hand_after: float


class ManufacturingOrderConsumptionResponse(BaseModel):
    manufacturing_order_id: int
    product_id: int
    order_quantity: int
    lines: list[MaterialConsumptionLineResponse]