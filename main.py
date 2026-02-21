from fastapi import FastAPI,Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from app.api.transactions import router as transaction_router
from app.api.returns import router as returns_router
from app.api.performance import router as performance_router

from app.utils.performance_tracker import tracker



PREFIX = "/blackrock/challenge/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracker.start()
    yield


app = FastAPI(
    title="BlackRock Retirement API",
    description="Automated retirement savings through expense-based micro-investments",
    version="1.0.0"
)
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


@app.get("/",include_in_schema=False)
def home():
    return {
        "name": "BlackRock Retirement API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "parse": f"{PREFIX}/transactions:parse",
            "validator": f"{PREFIX}/transactions:validator",
            "filter": f"{PREFIX}/transactions:filter",
            "returns_nps": f"{PREFIX}/returns:nps",
            "returns_index": f"{PREFIX}/returns:index",
            "performance": f"{PREFIX}/performance"
        }
    }    
app.include_router(transaction_router,prefix=PREFIX)
app.include_router(returns_router,prefix=PREFIX)
app.include_router(performance_router,prefix=PREFIX)