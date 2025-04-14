from app.db.base import Base
from sqlalchemy import Column, Integer, String, Text, Float
import json

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    _products = Column("products", Text, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="pending")

    @property
    def products(self):
        return self.get_products()
    
    def set_products(self, products_list):
        self._products = json.dumps(products_list)  # Convert list of dicts to JSON string

    def get_products(self):
        return json.loads(self._products)  # Convert JSON string back to list of dicts
