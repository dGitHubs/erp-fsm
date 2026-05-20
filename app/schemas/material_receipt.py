from pydantic import BaseModel, Field


class MaterialReceiveRequest(BaseModel):
    quantity: float = Field(gt=0)
    reference: str | None = None