from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.orders.exceptions import exceptions

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(exceptions.InsufficientStockException)
    async def insufficient_stock_exception_handler(request: Request, exc: exceptions.InsufficientStockException):
        return JSONResponse(
            status_code=400,
            content={
                "error": "InsufficientStock",
                "product_id": exc.product_id,
                "available": exc.available,
                "requested": exc.requested,
                "message": str(exc),
            },
        )