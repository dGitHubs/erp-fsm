from pydantic import BaseModel


class ManufacturingOrderMaterialRequirementLineResponse(BaseModel):
    material_id: int
    quantity_per_product: float
    required_quantity: float


class ManufacturingOrderMaterialRequirementsResponse(BaseModel):
    manufacturing_order_id: int
    product_id: int
    order_quantity: int
    lines: list[ManufacturingOrderMaterialRequirementLineResponse]