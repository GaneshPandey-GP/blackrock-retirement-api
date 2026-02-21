from fastapi import APIRouter
from app.models.schemas import ReturnsRequest, ReturnsResponse
from app.services.return_calculator import calculate_returns, NPS_RATE, INDEX_RATE

router = APIRouter()

@router.post("/returns:nps", response_model=ReturnsResponse)
def nps_returns(request: ReturnsRequest):
    return calculate_returns(request, rate=NPS_RATE, is_nps=True)

@router.post("/returns:index", response_model=ReturnsResponse)
def index_returns(request: ReturnsRequest):
    return calculate_returns(request, rate=INDEX_RATE, is_nps=False)
