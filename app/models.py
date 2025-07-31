from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .database import Base

class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    apartment_id = Column(String, unique=True, index=True)
    apartment_uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    apartment_name = Column(String, nullable=False)
    apartment_address = Column(String, nullable=False)
    admin_email = Column(String, nullable=False)
    total_floors = Column(Integer)
    total_flats = Column(Integer)
    water_bill_mode = Column(Integer, nullable=False, default=0)  # 0=Meter based, 1=Tanker based
    created_at = Column(DateTime(timezone=True), server_default=func.now())

