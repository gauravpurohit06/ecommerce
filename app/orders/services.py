from sqlalchemy.orm import Session
from app.orders.exceptions.exceptions import InsufficientStockException
from app.products.models import Product
from app.orders.models import Order
from app.orders.schemas import OrderCreate, OrderItem
from app.products.services import ProductService
from typing import List
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        """
        Initializes the OrderService with a ProductService dependency.

        Args:
            product_service (ProductService): An instance of the ProductService.
        """
        self.product_service = ProductService()
    
    def create_order(self, db: Session, order_data: OrderCreate):
        """
        Creates a new order, validates stock, and updates product quantities.

        Args:
            db (Session): The database session.
            order_data (OrderCreate): The order creation data.

        Returns:
            Order: The newly created order object.

        Raises:
            InsufficientStockException: If there is not enough stock for any of the requested products.
            Exception: If any unexpected error occurs during the order creation process.
        """
        logger.info(f"Attempting to create a new order with data: {order_data}")
        order_items: List[OrderItem] = order_data.products
        order_by_product: dict = defaultdict(int)

        logger.info("Processing order items to aggregate quantities per product.")
        for item in order_items:
            order_by_product[item.product_id] += item.quantity
            logger.debug(f"Product ID: {item.product_id}, Requested Quantity: {item.quantity}, Current aggregated quantity: {order_by_product[item.product_id]}")

        product_ids: List[int] = list(order_by_product.keys())
        logger.info(f"Extracted product IDs from the order: {product_ids}")

        with db.begin():
            logger.info("Starting database transaction for order creation.")
            # Lock and update stocks
            logger.info(f"Attempting to lock product rows with IDs: {product_ids}")
            product_rows: List[Product] = self.product_service.lock_product_rows(db, product_ids)
            logger.info(f"Locked {len(product_rows)} product rows.")

            logger.info("Validating if all requested product IDs exist.")
            self.product_service.validate_product_ids(product_rows, product_ids)
            logger.info("All requested product IDs are valid.")

            logger.info("Checking and updating product stock levels.")
            for product_row in product_rows:
                quantity = order_by_product[product_row.id]
                stock = product_row.stock
                logger.debug(f"Checking stock for Product ID: {product_row.id}, Name: {product_row.name}, Current Stock: {stock}, Requested Quantity: {quantity}")

                if stock < quantity:
                    logger.warning(f"Insufficient stock detected for Product ID: {product_row.id}, Name: {product_row.name}. Available: {stock}, Requested: {quantity}")
                    raise InsufficientStockException(product_row.id, stock, quantity)
                else:
                    product_row.stock -= quantity
                    logger.info(f"Updated stock for Product ID: {product_row.id}, Name: {product_row.name}. New Stock: {product_row.stock}")

            # Create order
            order = Order(
                total_price=order_data.total_price,
                status="completed"
            )

            order.set_products([{"product_id": product_id, "quantity": quantity} for product_id, quantity in order_by_product.items()])

            db.add(order)

        db.refresh(order)
        
        return order