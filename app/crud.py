from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from fastapi import HTTPException
import re


def generate_apartment_id(db: Session, apartment_name: str) -> str:
    """Generate a unique apartment ID based on apartment name"""
    # Clean the apartment name: remove special characters and convert to uppercase
    clean_name = re.sub(r'[^a-zA-Z\s]', '', apartment_name.upper())
    
    # Split into words and get first letters or abbreviate
    words = clean_name.split()
    
    if len(words) == 1:
        # Single word: take first 6 characters
        base_id = words[0][:6]
    elif len(words) == 2:
        # Two words: take first 3 characters of each
        base_id = words[0][:3] + words[1][:3]
    elif len(words) >= 3:
        # Multiple words: take first 2 chars of first word, first char of others
        base_id = words[0][:2]
        for word in words[1:]:
            if word:  # Skip empty words
                base_id += word[0]
    else:
        base_id = "APT"
    
    # Ensure base_id is not empty and has reasonable length
    base_id = base_id[:8] if base_id else "APT"
    
    # Check for existing IDs with this base
    existing_ids = db.query(models.Apartment.apartment_id).filter(
        models.Apartment.apartment_id.ilike(f"{base_id}%")
    ).all()
    
    if not existing_ids:
        return base_id
    
    # Extract numbers from existing IDs and find the next available number
    existing_numbers = []
    for (existing_id,) in existing_ids:
        if existing_id == base_id:
            existing_numbers.append(0)  # Base ID without number
        else:
            # Try to extract number from the end
            match = re.search(r'-(\d+)$', existing_id)
            if match:
                existing_numbers.append(int(match.group(1)))
    
    if not existing_numbers:
        return base_id
    
    # Find next available number
    next_num = max(existing_numbers) + 1
    return f"{base_id}-{next_num:03d}"


def get_last_apartment_id(db: Session) -> str:
    """Get the next apartment ID in sequence (deprecated - use generate_apartment_id instead)"""
    last = db.query(models.Apartment).order_by(desc(models.Apartment.apartment_id)).first()
    
    if last:
        try:
            num = int(last.apartment_id.split('-')[1]) + 1
            return f"APT-{num:04d}"  # Format as APT-0001
        except (ValueError, IndexError):
            pass
    return "APT-0001"


def create_apartment(db: Session, apartment: schemas.ApartmentCreate):
    """Create a new apartment with auto-generated apartment_id"""
    # Generate unique apartment_id based on apartment name
    apartment_id = generate_apartment_id(db, apartment.apartment_name)
    
    db_apartment = models.Apartment(
        apartment_id=apartment_id,
        apartment_name=apartment.apartment_name,
        apartment_address=apartment.apartment_address,
        admin_email=apartment.admin_email
    )
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment


def get_all_apartments(db: Session):
    """Get all apartments"""
    return db.query(models.Apartment).all()


def get_apartment_by_id(db: Session, apartment_id: str):
    """Get apartment by apartment_id"""
    return db.query(models.Apartment).filter(models.Apartment.apartment_id == apartment_id).first()


def update_apartment(db: Session, apartment_id: str, apartment_update: schemas.ApartmentUpdate):
    """Update apartment by apartment_id"""
    # First check if apartment exists
    apartment = get_apartment_by_id(db, apartment_id)
    if not apartment:
        return None
    
    # Prepare update data (only include non-None values)
    update_data = apartment_update.model_dump(exclude_unset=True, exclude_none=True)
    
    if not update_data:
        return apartment  # No updates to make
    
    # If apartment name is being updated, regenerate apartment_id
    if 'apartment_name' in update_data:
        new_apartment_id = generate_apartment_id(db, update_data['apartment_name'])
        # Only update if the new ID is different and doesn't already exist
        if new_apartment_id != apartment.apartment_id:
            existing = get_apartment_by_id(db, new_apartment_id)
            if not existing:
                update_data['apartment_id'] = new_apartment_id
    
    # Update the apartment
    for key, value in update_data.items():
        setattr(apartment, key, value)
    
    db.commit()
    db.refresh(apartment)
    return apartment


def get_apartment_by_uuid(db: Session, apartment_uuid: str):
    """Get apartment by UUID"""
    return db.query(models.Apartment).filter(models.Apartment.id == apartment_uuid).first()


def delete_apartment_by_uuid(db: Session, apartment_uuid: str):
    """Delete apartment by UUID"""
    # First check if apartment exists
    apartment = get_apartment_by_uuid(db, apartment_uuid)
    if not apartment:
        return None
    
    # Delete the apartment
    db.delete(apartment)
    db.commit()
    return apartment


def delete_apartment(db: Session, apartment_id: str):
    """Delete apartment by apartment_id (legacy - use delete_apartment_by_uuid for consistency)"""
    # First check if apartment exists
    apartment = get_apartment_by_id(db, apartment_id)
    if not apartment:
        return None
    
    # Delete the apartment
    db.delete(apartment)
    db.commit()
    return apartment
