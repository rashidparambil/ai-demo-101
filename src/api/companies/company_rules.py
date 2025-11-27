from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import CompanyRules
from .db_models import CompanyRuleTable
from .database import get_db
from .company_rule_embedding import CompanyRuleEmbedding

# Create a router for company endpoints
rules_router = APIRouter(prefix="/company_rule", tags=["company_rule"])


@rules_router.post("/{company_id}",response_model=str)
def save_company_rule(companyRule: CompanyRules, company_id: int):
    print(f"Storing rules for company ID: {company_id}")
    companyRuleEmbedding = CompanyRuleEmbedding(company_id)
    companyRuleEmbedding.store_company_rules(companyRule.rules)
    return "Company rules stored successfully."
    
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

