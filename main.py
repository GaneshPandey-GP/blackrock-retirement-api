from fastapi import FastAPI
from app.api.transactions import router as transaction_router
from app.api.returns import router as returns_router
from app.api.performance import router as performance_router

from app.utils.performance_tracker import tracker

app = FastAPI()

@app.on_event("startup")
def startup_event():
    tracker.start()
    
app.include_router(transaction_router)
app.include_router(returns_router)
app.include_router(performance_router)