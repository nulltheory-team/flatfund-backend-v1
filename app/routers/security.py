from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
import os

from ..database import get_db
from ..models import Security, User, UserRole
from ..schemas import SecurityCreate, SecurityResponse, SecurityListResponse

router = APIRouter(prefix="/api/v1/admin", tags=["security"])

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Extract and validate JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        flat_id: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        apt_id: str = payload.get("apt_id")
        role: str = payload.get("role")
        
        if flat_id is None or user_id is None or apt_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return {
        "user_id": int(user_id),
        "apt_id": apt_id,
        "flat_id": flat_id,
        "role": role,
        "user": user
    }

@router.post("/security", response_model=SecurityResponse)
async def create_security(
    request: SecurityCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new security personnel entry for the apartment.
    Only ADMIN users can create security entries.
    """
    # Check if user has ADMIN role
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only apartment administrators can add security personnel"
        )
    
    # Create security record
    security = Security(
        apartment_id=current_user["apt_id"],
        name=request.name.strip(),
        phone_number=request.phone_number.strip()
    )
    
    db.add(security)
    db.commit()
    db.refresh(security)
    
    return security

@router.get("/security", response_model=SecurityListResponse)
async def get_security_list(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all security personnel for the apartment.
    Any authenticated user (ADMIN, OWNER, TENANT) can view security list.
    """
    # Get all security records for the apartment
    security_list = db.query(Security).filter(
        Security.apartment_id == current_user["apt_id"]
    ).order_by(Security.created_at.desc()).all()
    
    return SecurityListResponse(
        status=True,
        message=f"Found {len(security_list)} security personnel",
        data=security_list
    )
