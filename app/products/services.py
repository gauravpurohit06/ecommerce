import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.products import models, schemas
from typing import List
from app.products.exceptions.exceptions import ProductNotFoundException
from app.products.models import Product

logger = logging.getLogger(__name__)

class ProductService:
    """
    Service class for handling product-related operations.
    """

    def get_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
        """
        Retrieves a list of products with optional pagination.

        Args:
            db (Session): The database session.
            skip (int): The number of products to skip. Defaults to 0.
            limit (int): The maximum number of products to retrieve. Defaults to 100.

        Returns:
            List[models.Product]: A list of product objects.
        """
        logger.info(f"Fetching products with skip: {skip}, limit: {limit}")
        products = db.query(models.Product).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(products)} products.")
        return products

    def create_product(self, db: Session, product: schemas.ProductCreate) -> models.Product:
        """
        Creates a new product in the database.

        Args:
            db (Session): The database session.
            product (schemas.ProductCreate): The product creation data.

        Returns:
            models.Product: The newly created product object.
        """
        logger.info(f"Attempting to create a new product with data: {product.dict()}")
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Created product with ID: {db_product.id}, Name: {db_product.name}")
        return db_product

    def lock_product_rows(self, db: Session, product_ids: List[int]) -> List[Product]:
        """
        Locks specific product rows in the database for update.

        Args:
            db (Session): The database session.
            product_ids (List[int]): A list of product IDs to lock.

        Returns:
            List[Product]: A list of locked product objects.
        """
        logger.info(f"Attempting to lock product rows with IDs: {product_ids}")
        stmt = select(Product).where(Product.id.in_(product_ids)).with_for_update()
        result = db.execute(stmt)
        locked_products = result.scalars().all()
        logger.info(f"Locked {len(locked_products)} product rows with IDs: {[p.id for p in locked_products]}")
        return locked_products

    def validate_product_ids(self, product_rows_from_db: List[Product], product_ids: List[int]):
        """
        Validates if all the provided product IDs exist in the database.

        Args:
            product_rows_from_db (List[Product]): List of product objects retrieved from the database.
            product_ids (List[int]): List of product IDs to validate.

        Raises:
            ProductNotFoundException: If any of the provided product IDs are not found in the database.
        """
        if len(product_rows_from_db) == 0:
            logger.warning(f"Product IDs not found in the database: {list(product_ids)}")
            raise ProductNotFoundException(list(product_ids))
        
        logger.info(f"Validating product IDs: {product_ids} against retrieved product rows.")
        product_ids_from_db: List[int] = [product_row.id for product_row in product_rows_from_db]

        product_ids_from_db_set = set(product_ids_from_db)
        product_ids_set = set(product_ids)

        invalid_product_ids = product_ids_set - product_ids_from_db_set

        if invalid_product_ids:
            logger.warning(f"Product IDs not found in the database: {list(invalid_product_ids)}")
            raise ProductNotFoundException(list(invalid_product_ids))
        else:
            logger.info("All provided product IDs are valid.")
            return