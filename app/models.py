from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import TypeDecorator, CHAR
import uuid
import enum
from .database import Base

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

class UserRole(enum.Enum):
    ADMIN = "admin"
    OWNER = "owner"
    TENANT = "tenant"

class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    apartment_id = Column(String, unique=True, index=True)
    apartment_uuid = Column(GUID(), unique=True, index=True, default=uuid.uuid4)
    apartment_name = Column(String, nullable=False)
    apartment_address = Column(String, nullable=False)
    admin_email = Column(String, nullable=False)
    total_floors = Column(Integer)
    total_flats = Column(Integer)
    water_bill_mode = Column(Integer, nullable=False, default=0)  # 0=Meter based, 1=Tanker based
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flat_uuid = Column(GUID(), unique=True, index=True, default=uuid.uuid4)
    flat_id = Column(String, index=True)
    apartment_uuid = Column(GUID(), index=True)
    apartment_id = Column(String, index=True)
    user_name = Column(String)
    user_phone_number = Column(String)
    user_email_id = Column(String, index=True)
    flat_number = Column(String)
    flat_floor = Column(String)  # Can be "B", "G", "1", "2", etc.
    role = Column(Enum(UserRole), default=UserRole.OWNER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False, index=True)
    apartment_id = Column(String, nullable=False)
    otp_code = Column(String, nullable=False)
    is_verified = Column(Integer, default=0)  # 0=Not verified, 1=Verified
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FlatmateInvitation(Base):
    __tablename__ = "flatmate_invitations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invitation_uuid = Column(GUID(), unique=True, index=True, default=uuid.uuid4)
    apartment_id = Column(String, nullable=False, index=True)
    flat_number = Column(String, nullable=False)
    floor = Column(String, nullable=False)  # Can be "B", "G", "1", "2", etc.
    invited_email = Column(String, nullable=False, index=True)
    invitation_code = Column(String, nullable=False, unique=True, index=True)  # 6-char alphanumeric
    invited_by_admin_email = Column(String, nullable=False)
    is_used = Column(Integer, default=0)  # 0=Not used, 1=Used
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

