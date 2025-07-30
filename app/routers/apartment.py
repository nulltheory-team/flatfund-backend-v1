from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(prefix="/api/v1/apartments", tags=["apartments"])

@router.post("/", response_model=schemas.ApartmentOut, status_code=status.HTTP_201_CREATED)
def create_apartment(
    apartment: schemas.ApartmentCreate, 
    db: Session = Depends(database.get_db)
):
    """Create a new apartment"""
    try:
        return crud.create_apartment(db, apartment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create apartment: {str(e)}"
        )

@router.get("/", response_model=list[schemas.ApartmentOut])
def get_apartments(db: Session = Depends(database.get_db)):
    """Get all apartments"""
    return crud.get_all_apartments(db)

@router.get("/{apartment_id}", response_model=schemas.ApartmentOut)
def get_apartment(apartment_id: str, db: Session = Depends(database.get_db)):
    """Get apartment by apartment_id"""
    apartment = crud.get_apartment_by_id(db, apartment_id)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with ID {apartment_id} not found"
        )
    return apartment

@router.put("/{apartment_id}", response_model=schemas.ApartmentOut)
def update_apartment(
    apartment_id: str,
    apartment_update: schemas.ApartmentUpdate,
    db: Session = Depends(database.get_db)
):
    """Update apartment by apartment_id"""
    apartment = crud.update_apartment(db, apartment_id, apartment_update)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with ID {apartment_id} not found"
        )
    return apartment

@router.delete("/uuid/{apartment_uuid}", response_model=schemas.ApartmentDeleted)
def delete_apartment_by_uuid(apartment_uuid: str, db: Session = Depends(database.get_db)):
    """Delete apartment by UUID for consistency"""
    apartment = crud.delete_apartment_by_uuid(db, apartment_uuid)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with UUID {apartment_uuid} not found"
        )
    return schemas.ApartmentDeleted(
        message="Apartment deleted successfully",
        apartment_id=apartment.apartment_id
    )

@router.delete("/{apartment_id}", response_model=schemas.ApartmentDeleted)
def delete_apartment(apartment_id: str, db: Session = Depends(database.get_db)):
    """Delete apartment by apartment_id (legacy endpoint)"""
    apartment = crud.delete_apartment(db, apartment_id)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with ID {apartment_id} not found"
        )
    return schemas.ApartmentDeleted(
        message="Apartment deleted successfully",
        apartment_id=apartment_id
    )