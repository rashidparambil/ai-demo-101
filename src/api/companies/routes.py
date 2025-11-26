from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import Company
from .db_models import CompanyTable
from .database import get_db

# Create a router for company endpoints
router = APIRouter(prefix="/company", tags=["company"])


@router.post("", response_model=Company)
def save_company(company: Company, db: Session = Depends(get_db)):
    """Save/create a new company and return it with an assigned id."""
    db_company = CompanyTable(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.get("/{company_id}", response_model=Company)
def retrieve_company(company_id: int, db: Session = Depends(get_db)):
    """Retrieve a company by id."""
    db_company = db.query(CompanyTable).filter(CompanyTable.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")
    return db_company


@router.get("", response_model=List[Company])
def list_companies(db: Session = Depends(get_db)):
    """List all companies."""
    companies = db.query(CompanyTable).all()
    return companies


@router.put("/{company_id}", response_model=Company)
def update_company(company_id: int, company: Company, db: Session = Depends(get_db)):
    """Update an existing company."""
    db_company = db.query(CompanyTable).filter(CompanyTable.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")
    
    for key, value in company.dict().items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company


@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company by id."""
    db_company = db.query(CompanyTable).filter(CompanyTable.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")
    
    db.delete(db_company)
    db.commit()
    return {"detail": "Company deleted"}


