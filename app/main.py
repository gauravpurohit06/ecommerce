from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.db.base import Base
from app.db.session import engine
from app.products.routers import router as product_router
from app.orders.routers import router as order_router

from app.products.exceptions.exception_handlers import register_exception_handlers as product_exception_handlers
from app.orders.exceptions.exception_handlers import register_exception_handlers as order_exception_handlers
import yaml
import logging.config

def setup_logging():
    with open("log_config.yaml", 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

app = FastAPI()

setup_logging()

Base.metadata.create_all(bind=engine)
app.include_router(product_router)
app.include_router(order_router)

order_exception_handlers(app)
product_exception_handlers(app)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    print (str(exc))
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )