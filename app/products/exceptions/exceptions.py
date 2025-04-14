class ProductNotFoundException(Exception):
  def __init__(self, product_ids: list[int]):
    self.product_ids = product_ids
    self.message = f"Products not found: {product_ids}"
    super().__init__(self.message)