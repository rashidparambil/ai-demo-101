from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from api.repository.database import get_db
from api.chat_bot.table_detail_repository import TableDetailsRepository
from api.chat_bot.models import TableDetails

router = APIRouter(prefix="/table-details", tags=["table-details"])

def get_repository(db: Session = Depends(get_db)) -> TableDetailsRepository:
    return TableDetailsRepository(db)

@router.post("", response_model=TableDetails)
def create_table_detail(
    table_description: str,
    repository: TableDetailsRepository = Depends(get_repository)
):
    """
    Create a new table detail.
    """
    try:
        return repository.add(table_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[TableDetails])
def get_all_table_details(
    repository: TableDetailsRepository = Depends(get_repository)
):
    """
    Get all table details.
    """
    try:
        return repository.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=TableDetails)
def get_table_detail(
    id: int,
    repository: TableDetailsRepository = Depends(get_repository)
):
    """
    Get a table detail by ID.
    """
    try:
        item = repository.get_by_id(id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Table detail with id {id} not found")
        return item
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
def delete_table_detail(
    id: int,
    repository: TableDetailsRepository = Depends(get_repository)
):
    """
    Delete a table detail by ID.
    """
    try:
        success = repository.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Table detail with id {id} not found")
        return {"detail": "Table detail deleted"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[TableDetails])
def search_table_details(
    query: str,
    limit: int = 5,
    repository: TableDetailsRepository = Depends(get_repository)
):
    """
    Search table details by semantic similarity.
    """
    try:
        return repository.search(query, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
