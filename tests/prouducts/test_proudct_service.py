import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.products.services import ProductService
from app.products import models, schemas
from app.products.exceptions.exceptions import ProductNotFoundException
from typing import List
from sqlalchemy.orm import Session

# Define a database URL for testing (in-memory SQLite for simplicity)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a test engine and session factory
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create the database tables for testing
def setup_test_database():
    models.Base.metadata.create_all(bind=test_engine)

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
def product_service():
    return ProductService()

# Sample product data for testing
def create_sample_products(db: Session) -> List[models.Product]:
    products_data = [
        {"name": "Product A", "description": "Description A", "price": 10.00, "stock": 100},
        {"name": "Product B", "description": "Description B", "price": 20.00, "stock": 50},
        {"name": "Product C", "description": "Description C", "price": 30.00, "stock": 25},
    ]
    products = [models.Product(**data) for data in products_data]
    db.add_all(products)
    db.commit()
    return products

def test_get_products(db: Session, product_service: ProductService):
    sample_products = create_sample_products(db)
    products = product_service.get_products(db)
    assert len(products) == len(sample_products)
    assert all(isinstance(p, models.Product) for p in products)

def test_create_product(db: Session, product_service: ProductService):
    product_data = schemas.ProductCreate(name="New Product", description="New Description", price=15.00, stock=75)
    created_product = product_service.create_product(db, product_data)
    assert created_product.id is not None
    assert created_product.name == "New Product"
    assert created_product.stock == 75
    db_product = db.query(models.Product).filter(models.Product.id == created_product.id).first()
    assert db_product is not None
    assert db_product.name == "New Product"

def test_lock_product_rows(db: Session, product_service: ProductService):
    sample_products = create_sample_products(db)
    ids_to_lock = [sample_products[0].id, sample_products[1].id]
    locked_products = product_service.lock_product_rows(db, ids_to_lock)
    assert len(locked_products) == 2
    assert all(p.id in ids_to_lock for p in locked_products)

def test_lock_product_rows_non_existent_ids(db: Session, product_service: ProductService):
    create_sample_products(db)
    ids_to_lock = [999, 1000]
    locked_products = product_service.lock_product_rows(db, ids_to_lock)
    assert len(locked_products) == 0

def test_validate_product_ids_all_exist(db: Session, product_service: ProductService):
    sample_products = create_sample_products(db)
    product_ids_to_validate = [p.id for p in sample_products]
    try:
        product_service.validate_product_ids(sample_products, product_ids_to_validate)
        assert True  # No exception should be raised
    except ProductNotFoundException:
        pytest.fail("ProductNotFoundException was raised unexpectedly")

def test_validate_product_ids_some_not_exist(db: Session, product_service: ProductService):
    sample_products = create_sample_products(db)
    product_ids_to_validate = [sample_products[0].id, 999, sample_products[2].id]
    with pytest.raises(ProductNotFoundException) as excinfo:
        product_service.validate_product_ids(sample_products, product_ids_to_validate)
    assert excinfo.value.product_ids == [999]

def test_validate_product_ids_none_exist(db: Session, product_service: ProductService):
    create_sample_products(db)
    product_ids_to_validate = [999, 1000]
    with pytest.raises(ProductNotFoundException) as excinfo:
        product_service.validate_product_ids([], product_ids_to_validate)
    assert set(excinfo.value.product_ids) == {999, 1000}