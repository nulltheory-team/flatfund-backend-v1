from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import random
import string
import os
from dotenv import load_dotenv

from ..database import get_db
from ..models import Apartment, User, OTPVerification, UserRole
from ..schemas import SendOTPRequest, VerifyOTPRequest, AuthResponse

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["authentication"])

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Brevo Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

def generate_otp() -> str:
    """Generate a 4-digit OTP"""
    return ''.join(random.choices(string.digits, k=4))

def send_otp_email_mock(email: str, otp: str, apartment_name: str):
    """Mock email sending for testing - just prints the OTP"""
    print(f"📧 Mock Email to {email}")
    print(f"Subject: FlatFund - Your OTP Code for {apartment_name}")
    print(f"OTP Code: {otp}")
    print(f"This is a mock email for testing. In production, this would be sent via Brevo.")
    return True

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signin")
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Send OTP to admin email for apartment signin (Development/Testing version)"""
    
    # Verify apartment exists and email matches
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id,
        Apartment.admin_email == request.admin_email
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found or email doesn't match"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes expiry
    
    # Delete any existing OTP for this email/apartment combination
    db.query(OTPVerification).filter(
        OTPVerification.email == request.admin_email,
        OTPVerification.apartment_id == request.apt_id
    ).delete()
    
    # Create new OTP record
    otp_record = OTPVerification(
        email=request.admin_email,
        apartment_id=request.apt_id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()
    
    # Send OTP via mock email (for testing)
    try:
        send_otp_email_mock(request.admin_email, otp_code, apartment.apartment_name)
        
        # In development mode, return the OTP for testing
        is_development = os.getenv("DEBUG", "false").lower() == "true" or os.getenv("ENVIRONMENT", "development") == "development"
        
        response = {
            "status": True,
            "message": "OTP sent successfully to your email",
            "expires_in_minutes": 10
        }
        
        # Only include OTP in response during development/testing
        if is_development or not BREVO_API_KEY:
            response["otp_for_testing"] = otp_code
            response["note"] = "OTP included for testing purposes only. This will not appear in production."
        
        return response
        
    except Exception as e:
        # Rollback OTP record if email fails
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and return authentication token"""
    
    # Get apartment details
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id,
        Apartment.admin_email == request.admin_email
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found or email doesn't match"
        )
    
    # Verify OTP
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.email == request.admin_email,
        OTPVerification.apartment_id == request.apt_id,
        OTPVerification.otp_code == request.otp,
        OTPVerification.is_verified == 0,
        OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as verified
    otp_record.is_verified = 1
    db.commit()
    
    # Check if user exists, if not create one
    user = db.query(User).filter(
        User.user_email_id == request.admin_email,
        User.apartment_id == request.apt_id
    ).first()
    
    if not user:
        # Create new admin user
        user = User(
            flat_id=f"admin_{apartment.apartment_id}",
            apartment_uuid=apartment.apartment_uuid,
            apartment_id=apartment.apartment_id,
            user_email_id=request.admin_email,
            role=UserRole.ADMIN
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT token
    token_data = {
        "user_id": str(user.id),
        "apt_id": apartment.apartment_id,
        "apt_uuid": str(apartment.apartment_uuid),
        "role": user.role.value,
        "email": user.user_email_id
    }
    access_token = create_access_token(token_data)
    
    # Check if user details are filled
    is_all_user_details_filled = bool(
        user.user_name and 
        user.user_phone_number and 
        user.flat_number is not None and 
        user.flat_floor is not None
    )
    
    response_data = {
        "apt_id": apartment.apartment_id,
        "apt_uuid": str(apartment.apartment_uuid),
        "flat_id": user.flat_id,
        "flat_uuid": str(user.flat_uuid),
        "user_id": f"user_{user.id}",
        "is_all_user_details_filled": is_all_user_details_filled,
        "role": user.role.value
    }
    
    return AuthResponse(
        status=True,
        message="OTP verified successfully",
        token=access_token,
        data=response_data
    )
