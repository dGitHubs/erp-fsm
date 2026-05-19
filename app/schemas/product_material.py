from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductMaterialCreate(BaseModel):
    product_id: int
    material_id: int
    quantity: float = Field(gt=0)


class ProductMaterialResponse(BaseModel):
    id: int
    product_id: int
    material_id: int
    quantity: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)