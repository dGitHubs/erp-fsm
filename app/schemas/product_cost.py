from pydantic import BaseModel, ConfigDict


class ProductMaterialCostLineResponse(BaseModel):
    material_id: int
    quantity: float
    unit_cost: float
    line_cost: float

    model_config = ConfigDict(from_attributes=True)


class ProductMaterialCostResponse(BaseModel):
    product_id: int
    material_cost: float
    lines: list[ProductMaterialCostLineResponse]