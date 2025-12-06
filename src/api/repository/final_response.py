from typing import List

from pydantic import BaseModel, ConfigDict

class FieldValidation(BaseModel):
    message: str


class Rule(BaseModel):
    rule_id: int
    description: str
    status: str

class ExtractedField(BaseModel):
    customer_name: str
    customer_account: str
    amount_paid: float
    balance_amount: float
    transformtion_rules: List[Rule]
    validation_rules: List[Rule]
    field_validations: List[FieldValidation]

class FinalResponse(BaseModel):
    model_config = ConfigDict(
        # This is the line that fixes the error
        arbitrary_types_allowed=True 
    )
    client_id: int
    client_name: str
    process_type: int
    extracted_fields: List[ExtractedField]




