from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    apartment_id = Column(String, unique=True, index=True)
    apartment_name = Column(String, nullable=False)
    apartment_address = Column(String, nullable=False)
    admin_email = Column(String, nullable=False)