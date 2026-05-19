from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MaterialUnit(StrEnum):
    UNIT = "unit"
    INCH = "inch"
    FOOT = "foot"
    SQUARE_FOOT = "square_foot"
    CUBIC_FOOT = "cubic_foot"


class MaterialCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
    unit: MaterialUnit = MaterialUnit.UNIT
    unit_cost: float = Field(ge=0)


class MaterialResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    unit: MaterialUnit
    unit_cost: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)