from pydantic import BaseModel, Json
from typing import List, Dict


class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderBase(BaseModel):
    products: List[OrderItem]
    total_price: float

class OrderCreate(OrderBase):
    pass

class Order(OrderCreate):
    id: int
    status: str

    class Config:
        orm_mode = True
