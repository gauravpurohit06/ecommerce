from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.products import schemas
from app.products.services import ProductService
from typing import List

router = APIRouter(prefix='/products')

@router.get("/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    product_service = ProductService()
    return product_service.get_products(db=db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    product_service = ProductService()
    return product_service.create_product(db=db, product=product)