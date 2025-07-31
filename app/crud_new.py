from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from fastapi import HTTPException


def create_apartment(db: Session, apartment: schemas.ApartmentCreate):
    """Create a new apartment with auto-increment apartment_id"""
    db_apartment = models.Apartment(
        apartment_name=apartment.apartment_name,
        apartment_address=apartment.apartment_address,
        admin_email=apartment.admin_email,
        total_floors=apartment.total_floors,
        total_flats=apartment.total_flats,
        water_bill_mode=apartment.water_bill_mode
    )
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment


def get_all_apartments(db: Session):
    """Get all apartments"""
    return db.query(models.Apartment).all()


def get_apartment_by_id(db: Session, apartment_id: int):
    """Get apartment by apartment_id"""
    return db.query(models.Apartment).filter(models.Apartment.apartment_id == apartment_id).first()


def get_apartment_by_uuid(db: Session, apartment_uuid: str):
    """Get apartment by apartment_uuid"""
    return db.query(models.Apartment).filter(models.Apartment.apartment_uuid == apartment_uuid).first()


def update_apartment(db: Session, apartment_id: int, apartment_update: schemas.ApartmentUpdate):
    """Update apartment by apartment_id"""
    # First check if apartment exists
    apartment = get_apartment_by_id(db, apartment_id)
    if not apartment:
        return None
    
    # Prepare update data (only include non-None values)
    update_data = apartment_update.model_dump(exclude_unset=True, exclude_none=True)
    
    if not update_data:
        return apartment  # No updates to make
    
    # Update the apartment
    for key, value in update_data.items():
        setattr(apartment, key, value)
    
    db.commit()
    db.refresh(apartment)
    return apartment


def delete_apartment_by_id(db: Session, apartment_id: int):
    """Delete apartment by apartment_id"""
    # First check if apartment exists
    apartment = get_apartment_by_id(db, apartment_id)
    if not apartment:
        return None
    
    db.delete(apartment)
    db.commit()
    return apartment


def delete_apartment_by_uuid(db: Session, apartment_uuid: str):
    """Delete apartment by apartment_uuid"""
    # First check if apartment exists
    apartment = get_apartment_by_uuid(db, apartment_uuid)
    if not apartment:
        return None
    
    db.delete(apartment)
    db.commit()
    return apartment
