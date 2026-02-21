from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from app.api.transactions import router as transaction_router
from app.api.returns import router as returns_router
from app.api.performance import router as performance_router

from app.utils.performance_tracker import tracker

app = FastAPI(
    title="BlackRock Retirement API",
    description="Automated retirement savings through expense-based micro-investments",
    version="1.0.0"
)

PREFIX = "/blackrock/challenge/v1"


@app.on_event("startup")
def startup():
    tracker.start()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
    
app.include_router(transaction_router,prefix=PREFIX)
app.include_router(returns_router,prefix=PREFIX)
app.include_router(performance_router,prefix=PREFIX)