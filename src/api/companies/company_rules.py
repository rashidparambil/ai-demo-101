from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import CompanyRule
from .db_models import CompanyRuleTable
from .database import get_db

# Create a router for company endpoints
rules_router = APIRouter(prefix="/company/rule", tags=["company_rule"])

'''
@router.post("", response_model=CompanyRule)
def save_company(rule: CompanyRule, db: Session = Depends(get_db)):
    """Save/create a new company and return it with an assigned id."""
    db_company = CompanyRuleTable(**rule.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company
'''
'''
@router.get("/{company_id}", response_model=CompanyRule)
def retrieve_company(company_id: int, db: Session = Depends(get_db)):
    """Retrieve a company by id."""
    db_company = db.query(CompanyRuleTable).filter(CompanyRuleTable.company_id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")
    return db_company

'''
@rules_router.get("")
def list_companies(db: Session = Depends(get_db)):
    """List all companies."""
    companies = db.query(CompanyRuleTable).all()
    return companies

