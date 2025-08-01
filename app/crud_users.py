from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional
import uuid

def get_user_by_email_and_apt(db: Session, email: str, apartment_id: str) -> Optional[models.User]:
    """Get user by email and apartment ID"""
    return db.query(models.User).filter(
        models.User.user_email_id == email,
        models.User.apartment_id == apartment_id
    ).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    db_user = models.User(
        flat_id=user.flat_id,
        apartment_uuid=user.apartment_uuid,
        apartment_id=user.apartment_id,
        user_name=user.user_name,
        user_phone_number=user.user_phone_number,
        user_email_id=user.user_email_id,
        flat_number=user.flat_number,
        flat_floor=user.flat_floor,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: dict) -> Optional[models.User]:
    """Update user details"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_update.items():
            if hasattr(db_user, key) and value is not None:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def get_users_by_apartment(db: Session, apartment_id: str, skip: int = 0, limit: int = 100):
    """Get all users in an apartment"""
    return db.query(models.User).filter(
        models.User.apartment_id == apartment_id
    ).offset(skip).limit(limit).all()
