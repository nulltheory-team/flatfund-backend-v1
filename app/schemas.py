from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    TENANT = "tenant"

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

# OTP and Authentication Schemas
class SendOTPRequest(BaseModel):
    apt_id: str
    admin_email: EmailStr

class VerifyOTPRequest(BaseModel):
    apt_id: str
    admin_email: EmailStr
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    status: bool
    message: str
    token: TokenResponse
    data: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserCreate(BaseModel):
    flat_id: str
    apartment_uuid: UUID
    apartment_id: str
    user_name: Optional[str] = None
    user_phone_number: Optional[str] = None
    user_email_id: str
    flat_number: Optional[str] = None
    flat_floor: Optional[str] = None  # Can be "B", "G", "1", "2", etc.
    role: UserRole = UserRole.OWNER

class UserOut(BaseModel):
    id: int
    flat_uuid: UUID
    flat_id: str
    apartment_uuid: UUID
    apartment_id: str
    user_name: Optional[str]
    user_phone_number: Optional[str]
    user_email_id: str
    flat_number: Optional[str]
    flat_floor: Optional[str]  # Can be "B", "G", "1", "2", etc.
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Additional Tenant Assignment Schema (for existing flats)
class AssignTenantRequest(BaseModel):
    apt_id: str
    flat_id: str
    tenant_email_id: EmailStr

class AssignTenantResponse(BaseModel):
    status: bool
    message: str
    data: dict

# Flatmate Invitation Schemas
class InviteFlatmateRequest(BaseModel):
    """
    Request to invite a new flatmate with floor information.
    Supports Indian apartment floor naming conventions.
    """
    apt_id: str = Field(..., description="Apartment ID", example="PRESTIGE_HEIGHTS")
    flat_number: str = Field(..., description="Flat number", example="101")
    floor: str = Field(
        ..., 
        description="Floor designation supporting Indian conventions: 'B' (Basement), 'G' (Ground), '1', '2', '3'... (numbered floors), 'M' (Mezzanine), 'UG' (Upper Ground)",
        example="G"
    )
    owner_email_id: EmailStr = Field(..., description="Email of the inviting owner/admin", example="owner@example.com")

class InviteFlatmateResponse(BaseModel):
    """Response after sending flatmate invitation"""
    status: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: dict = Field(..., description="Invitation details including 6-character code and floor information")

# Flatmate Signup Schemas  
class FlatmateSignupRequest(BaseModel):
    """
    Request to signup as a flatmate using invitation code.
    Floor information is automatically inherited from the invitation.
    """
    apartment_name: str = Field(..., description="Name of the apartment", example="Prestige Heights")
    apt_id: str = Field(..., description="Apartment ID", example="PRESTIGE_HEIGHTS")
    flat_number: str = Field(..., description="Flat number (must match invitation)", example="101")
    email_id: EmailStr = Field(..., description="Email address (must match invitation)", example="tenant@example.com")
    unique_code: str = Field(..., description="6-character invitation code received via email", example="ABC123")

class FlatmateSignupResponse(BaseModel):
    """Response after successful flatmate signup"""
    status: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Welcome message")
    data: dict = Field(..., description="User details including inherited floor information")

# Login Flow Schemas
class SelectApartmentRequest(BaseModel):
    email_id: EmailStr

class SelectApartmentResponse(BaseModel):
    status: bool
    message: str
    apartments: list

class LoginRequest(BaseModel):
    apt_id: str
    email_id: EmailStr

class LoginResponse(BaseModel):
    status: bool
    message: str
    expires_in_minutes: int

# Security Schemas
class SecurityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=15)

class SecurityResponse(BaseModel):
    id: int
    apartment_id: str
    name: str
    phone_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SecurityListResponse(BaseModel):
    status: bool
    message: str
    data: list[SecurityResponse]

# Suggested Flat Details Schema (for OTP response)
class SuggestedFlatDetails(BaseModel):
    flat_number: Optional[str] = None
    flat_floor: Optional[str] = None

# Update User Details Schemas
class UpdateFlatmateDetailsRequest(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    user_phone_number: str = Field(..., min_length=10, max_length=15)
    flat_number: Optional[str] = Field(None, max_length=20)
    flat_floor: Optional[str] = Field(None, max_length=10)

class UpdateFlatmateDetailsResponse(BaseModel):
    message: str
    user_name: str
    user_phone_number: str
    flat_number: Optional[str]
    flat_floor: Optional[str]
    is_all_user_details_filled: bool

class GetFlatmateDetailsResponse(BaseModel):
    user_name: Optional[str]
    user_phone_number: Optional[str]
    user_email: str
    flat_id: str
    apartment_name: str
    apartment_address: str
    flat_number: Optional[str]
    flat_floor: Optional[str]
    role: str
    is_all_user_details_filled: bool