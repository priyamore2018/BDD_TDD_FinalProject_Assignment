"""
tests/factories.py
Task 1: Factory class for generating fake Product data in tests.

Uses Python's built-in random and string modules — no third-party
libraries required. Install nothing extra.
"""
import random
import string
from decimal import Decimal

from service.models import Product, Category

# ── word pools used to build realistic-looking fake data ─────────────
_ADJECTIVES = [
    "Heavy-Duty", "Professional", "Compact", "Premium", "Classic",
    "Lightweight", "Industrial", "Portable", "Deluxe", "Standard",
]
_NOUNS = [
    "Hammer", "Drill", "Wrench", "Saw", "Screwdriver",
    "Spanner", "Chisel", "Pliers", "Level", "Clamp",
    "Pan", "Knife", "Bowl", "Mug", "Shelf",
    "Jacket", "Shirt", "Boots", "Hat", "Gloves",
]
_DESCRIPTIONS = [
    "A high-quality product for everyday use.",
    "Designed for professionals who demand the best.",
    "Durable construction ensures a long service life.",
    "An essential item for any home or workshop.",
    "Compact design makes it easy to store and carry.",
    "Precision-engineered for maximum performance.",
    "Trusted by tradespeople for over 20 years.",
    "Lightweight yet incredibly strong.",
]


def _fake_name() -> str:
    return f"{random.choice(_ADJECTIVES)} {random.choice(_NOUNS)}"


def _fake_description() -> str:
    return random.choice(_DESCRIPTIONS)


def _fake_price() -> Decimal:
    return Decimal(str(round(random.uniform(1.99, 299.99), 2)))


def _fake_available() -> bool:
    return random.random() < 0.75          # 75 % chance of being available


def _fake_category() -> Category:
    return random.choice(list(Category))


######################################################################
# Task 1 — ProductFactory
######################################################################

class ProductFactory:
    """
    Generates fake Product objects for use in unit and integration tests.

    Usage:
        product  = ProductFactory.create()           # one Product
        products = ProductFactory.create_batch(5)    # list of 5 Products

    Override any field by passing it as a keyword argument:
        product = ProductFactory.create(name="Hammer", category=Category.TOOLS)
    """

    @staticmethod
    def create(**overrides) -> Product:
        """
        Build and return a single fake Product.
        Any keyword argument will override the generated value.

        Example:
            product = ProductFactory.create(name="Hammer", available=True)
        """
        product = Product()

        product.name        = overrides.get("name",        _fake_name())
        product.description = overrides.get("description", _fake_description())
        product.price       = overrides.get("price",       _fake_price())
        product.available   = overrides.get("available",   _fake_available())
        product.category    = overrides.get("category",    _fake_category())

        # Accept a category passed as a string (e.g. "TOOLS") and convert it
        if isinstance(product.category, str):
            product.category = Category[product.category.upper()]

        # Accept a price passed as a string or float and normalise to Decimal
        if not isinstance(product.price, Decimal):
            product.price = Decimal(str(product.price))

        return product

    @staticmethod
    def create_batch(count: int, **overrides) -> list:
        """
        Build and return a list of *count* fake Products.

        Example:
            products = ProductFactory.create_batch(10, available=True)
        """
        return [ProductFactory.create(**overrides) for _ in range(count)]


# ── Convenience aliases ───────────────────────────────────────────────

def fake_product(**overrides) -> Product:
    """Shorthand for ProductFactory.create(**overrides)."""
    return ProductFactory.create(**overrides)


def fake_products(count: int = 5, **overrides) -> list:
    """Shorthand for ProductFactory.create_batch(count, **overrides)."""
    return ProductFactory.create_batch(count, **overrides)
