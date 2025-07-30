#!/usr/bin/env python3
"""
Migration script to update existing apartment records with proper apartment_id values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base, Apartment
from app.crud import generate_apartment_id
from sqlalchemy.orm import sessionmaker
import re

def clean_apartment_name(name):
    """Clean apartment name for ID generation"""
    return re.sub(r'[^a-zA-Z\s]', '', name.upper())

def create_apartment_id_from_name(name):
    """Create apartment ID from name using same logic as generate_apartment_id but without DB check"""
    clean_name = clean_apartment_name(name)
    words = clean_name.split()
    
    if len(words) == 1:
        base_id = words[0][:6]
    elif len(words) == 2:
        base_id = words[0][:3] + words[1][:3]
    elif len(words) >= 3:
        base_id = words[0][:2]
        for word in words[1:]:
            if word:
                base_id += word[0]
    else:
        base_id = "APT"
    
    return base_id[:8] if base_id else "APT"

def main():
    print("🔄 Starting apartment_id migration...")
    
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Get all apartments with None apartment_id
        apartments = session.query(Apartment).filter(Apartment.apartment_id.is_(None)).all()
        
        if not apartments:
            print("✅ No apartments found with None apartment_id")
            return
        
        print(f"📋 Found {len(apartments)} apartments with None apartment_id")
        
        # Track used IDs to avoid duplicates
        used_ids = set()
        
        # Get existing apartment_ids to avoid conflicts
        existing_apartments = session.query(Apartment).filter(Apartment.apartment_id.isnot(None)).all()
        for apt in existing_apartments:
            used_ids.add(apt.apartment_id)
        
        # Update each apartment
        for i, apartment in enumerate(apartments, 1):
            base_id = create_apartment_id_from_name(apartment.apartment_name)
            apartment_id = base_id
            
            # Handle duplicates by adding numbers
            counter = 1
            while apartment_id in used_ids:
                apartment_id = f"{base_id}-{counter:03d}"
                counter += 1
            
            # Update the apartment
            apartment.apartment_id = apartment_id
            used_ids.add(apartment_id)
            
            print(f"  {i:2d}. '{apartment.apartment_name}' -> '{apartment_id}'")
        
        # Commit changes
        session.commit()
        print(f"✅ Successfully updated {len(apartments)} apartments")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
        return 1
    
    finally:
        session.close()
    
    print("🎉 Migration completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
