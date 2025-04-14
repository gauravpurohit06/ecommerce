class InsufficientStockException(Exception):
    def __init__(self, product_id: int, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(f"Insufficient stock for product {product_id}: Available={available}, Requested={requested}")