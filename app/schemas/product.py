from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProductUnit(StrEnum):
    UNIT = "unit"
    INCH = "inch"
    FOOT = "foot"
    SQUARE_FOOT = "square_foot"


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
    unit: ProductUnit = ProductUnit.UNIT
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
    depth: float | None = Field(default=None, gt=0)


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    unit: ProductUnit
    width: float | None
    height: float | None
    depth: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)