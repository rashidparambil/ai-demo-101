from typing import List

class FieldValidation:
    message: str


class Rule:
    rule_id: int
    description: str
    status: str

class ExtractedField:
    customer_name: str
    customer_account: str
    amount_paid: float
    balance_amount: float
    transformtion_rules: List[Rule]
    validation_rules: List[Rule]
    field_validations: List[FieldValidation]

class FinalResponse:
    client_id: int
    client_name: str
    process_type: int
    extracted_fields: List[ExtractedField]




