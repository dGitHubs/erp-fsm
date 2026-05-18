from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr | None
    phone: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
