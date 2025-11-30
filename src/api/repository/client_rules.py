from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import ClientRules
from .client_rule_embedding import ClientRuleEmbedding

# Create a router for client endpoints
rules_router = APIRouter(prefix="/client_rule", tags=["client_rule"])

@rules_router.post("/{client_id}",response_model=str)
def save_client_rule(clientRule: ClientRules, client_id: int):
    print(f"Storing rules for client ID: {client_id}")
    clientRuleEmbedding = ClientRuleEmbedding(client_id)
    clientRuleEmbedding.store_client_rules(clientRule.process_type, clientRule.rules)
    return "Client rules stored successfully."

@rules_router.get("/{client_id}")
def list_client_rules(client_id: int):
    print(f"get client rules for client ID: {client_id}")
    clientRuleEmbedding = ClientRuleEmbedding(client_id)
    return clientRuleEmbedding.search_rules(return_all=True, k=100,include_embeddings=True)

