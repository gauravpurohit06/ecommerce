from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.orders.schemas import OrderCreate, Order

from app.orders.services import OrderService
from app.db.session import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    order_service: OrderService = OrderService()
    return order_service.create_order(db=db, order_data=order)