from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class ApartmentCreate(BaseModel):
    apartment_name: str
    apartment_address: str
    admin_email: EmailStr
    total_floors: Optional[int] = None
    total_flats: Optional[int] = None
    water_bill_mode: int = 0  # Default to meter based

class ApartmentUpdate(BaseModel):
    apartment_name: Optional[str] = None
    apartment_address: Optional[str] = None
    admin_email: Optional[EmailStr] = None
    total_floors: Optional[int] = None
    total_flats: Optional[int] = None
    water_bill_mode: Optional[int] = None

class ApartmentOut(BaseModel):
    id: int
    apartment_id: str
    apartment_uuid: UUID
    apartment_name: str
    apartment_address: str
    admin_email: str
    total_floors: Optional[int]
    total_flats: Optional[int]
    water_bill_mode: int
    created_at: datetime

    class Config:
        from_attributes = True

class ApartmentDeleted(BaseModel):
    message: str
    apartment_id: str