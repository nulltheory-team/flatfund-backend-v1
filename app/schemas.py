from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class ApartmentCreate(BaseModel):
    apartment_name: str
    apartment_address: str
    admin_email: EmailStr

class ApartmentUpdate(BaseModel):
    apartment_name: Optional[str] = None
    apartment_address: Optional[str] = None
    admin_email: Optional[EmailStr] = None

class ApartmentOut(BaseModel):
    id: UUID
    apartment_id: str
    apartment_name: str
    apartment_address: str
    admin_email: str

    class Config:
        from_attributes = True

class ApartmentDeleted(BaseModel):
    message: str
    apartment_id: str