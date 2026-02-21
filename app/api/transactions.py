from app.services.temporal_filter import filter_transactions
from fastapi import APIRouter
from app.models.schemas import TransactionParseRequest,TransactionFilterResponse,TransactionFilterRequest
from app.services.transaction_builder import build_transactions
from app.services.transaction_validator import validate_transactions
from app.models.schemas import TransactionValidatorRequest

router = APIRouter(prefix="/blackrock/challenge/v1")

@router.post("/transactions:parse")
def parse_transactions(request: TransactionParseRequest):
    result = build_transactions(request.expenses)
    return result


@router.post("/transactions:validator")
def validate(request: TransactionValidatorRequest):
    result = validate_transactions(request.wage, request.transactions)
    return result

@router.post("/transactions:filter", response_model=TransactionFilterResponse)
def filter_transactions_endpoint(request: TransactionFilterRequest):
    return filter_transactions(request)