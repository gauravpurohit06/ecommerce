# app/product/handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status
from .exceptions import ProductNotFoundException

def register_exception_handlers(app):
  @app.exception_handler(ProductNotFoundException)
  async def product_not_found_exception_handler(request: Request, exc: ProductNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "ProductNotFound",
            "missing_product_ids": exc.product_ids,
            "message": exc.message
        }
    )
