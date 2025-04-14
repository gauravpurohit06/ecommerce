# ecommerce/tests/orders/test_order_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.orders.services import OrderService
from app.products.services import ProductService
from app.orders import models as order_models
from app.products import models as product_models
from app.orders import schemas as order_schemas
from app.orders.exceptions.exceptions import InsufficientStockException
from app.products.exceptions.exceptions import ProductNotFoundException
from typing import List
from unittest.mock import MagicMock

# Define a test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a test engine and session factory
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create the database tables for testing
def setup_test_database():
    order_models.Base.metadata.create_all(bind=test_engine)
    product_models.Base.metadata.create_all(bind=test_engine)

# Dependency to get a test database session
@pytest.fixture(scope="function")
def db():
    setup_test_database()
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def order_service():
    return OrderService()

@pytest.fixture(scope="function")
def product_service_mock():
    # Create a mock ProductService to control its behavior
    mock = MagicMock(spec=ProductService)
    return mock

# Helper function to create product rows in the test database
def create_test_products(db: Session) -> List[product_models.Product]:
    products_data = [
        {"name": "Product A", "description": "Description A", "price": 10.00, "stock": 10},
        {"name": "Product B", "description": "Description B", "price": 20.00, "stock": 5},
    ]
    products = [product_models.Product(**data) for data in products_data]
    db.add_all(products)
    db.commit()
    return products

def test_create_order_insufficient_stock(db: Session, order_service: OrderService):
    create_test_products(db)
    order_data = order_schemas.OrderCreate(
        total_price=float("200.00"),
        products=[
            order_schemas.OrderItem(product_id=1, quantity=15),
        ]
    )

    with pytest.raises(InsufficientStockException) as excinfo:
        order_service.create_order(db, order_data)
    assert excinfo.value.product_id == 1
    assert excinfo.value.available == 10
    assert excinfo.value.requested == 15

    # Verify that the stock was not updated
    product_a = db.query(product_models.Product).filter(product_models.Product.id == 1).first()
    assert product_a.stock == 10

def test_create_order_success(db: Session, order_service: OrderService):
    test_products = create_test_products(db)
    order_data = order_schemas.OrderCreate(
        total_price=float("30.00"),
        products=[
            order_schemas.OrderItem(product_id=1, quantity=2),
            order_schemas.OrderItem(product_id=2, quantity=1),
        ]
    )

    created_order = order_service.create_order(db, order_data)

    assert created_order.id is not None
    assert created_order.total_price == float("30.00")
    assert created_order.status == "completed"
    assert len(created_order.products) == 2
    assert any(item['product_id'] == 1 and item['quantity'] == 2 for item in created_order.products)
    assert any(item['product_id'] == 2 and item['quantity'] == 1 for item in created_order.products)

    # Verify that the stock was updated
    product_a = db.query(product_models.Product).filter(product_models.Product.id == 1).first()
    product_b = db.query(product_models.Product).filter(product_models.Product.id == 2).first()
    assert product_a.stock == 8
    assert product_b.stock == 4

def test_create_order_invalid_product_ids(db: Session, order_service: OrderService, product_service_mock: MagicMock):
    # Configure the mock ProductService to raise ProductNotFoundException
    product_service_mock.lock_product_rows.return_value = []
    product_service_mock.validate_product_ids.side_effect = ProductNotFoundException([999])
    order_service.product_service = product_service_mock

    order_data = order_schemas.OrderCreate(
        total_price=float("10.00"),
        products=[
            order_schemas.OrderItem(product_id=999, quantity=1),
        ]
    )

    with pytest.raises(ProductNotFoundException) as excinfo:
        order_service.create_order(db, order_data)
    assert excinfo.value.product_ids == [999]

    # Verify that lock_product_rows and validate_product_ids were called
    product_service_mock.lock_product_rows.assert_called_once_with(db, [999])
    product_service_mock.validate_product_ids.assert_called_once_with([], [999])