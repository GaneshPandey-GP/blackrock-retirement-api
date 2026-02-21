from fastapi import APIRouter
from app.utils.performance_tracker import tracker

router = APIRouter()

@router.get("/performance")
def get_performance():
    return tracker.get_metrics()