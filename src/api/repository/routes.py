from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import Client
from .db_models import ClientTable
from .database import get_db

# Create a router for client endpoints
router = APIRouter(prefix="/client", tags=["client"])


@router.post("", response_model=Client)
def save_client(client: Client, db: Session = Depends(get_db)):
    """Save/create a new client and return it with an assigned id."""
    db_client = ClientTable(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/{client_id}", response_model=Client)
def retrieve_client(client_id: int, db: Session = Depends(get_db)):
    """Retrieve a client by id."""
    db_client = db.query(ClientTable).filter(ClientTable.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Client with id {client_id} not found")
    return db_client


@router.get("", response_model=List[Client])
def list_clients(db: Session = Depends(get_db)):
    """List all clients."""
    clients = db.query(ClientTable).all()
    return clients


@router.put("/{client_id}", response_model=Client)
def update_client(client_id: int, client: Client, db: Session = Depends(get_db)):
    """Update an existing client."""
    db_client = db.query(ClientTable).filter(ClientTable.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Client with id {client_id} not found")
    
    for key, value in client.dict().items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client by id."""
    db_client = db.query(ClientTable).filter(ClientTable.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Client with id {client_id} not found")
    
    db.delete(db_client)
    db.commit()
    return {"detail": "Client deleted"}


