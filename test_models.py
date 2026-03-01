"""
tests/test_models.py
Task 2: Unit tests for the Product model.

Covers: Read / Update / Delete / List All /
        Find by Name / Find by Category / Find by Availability
"""
import os
import sys
import tempfile
import sqlite3
import unittest
from decimal import Decimal

# Ensure the project root is on the path when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import service.models as models_module
from service.models import Product, Category, DataValidationError
from tests.factories import ProductFactory, fake_product

# ── shared temp database (one file for the whole test run) ───────────
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
TEST_DB = _tmp.name


def reset_db():
    """Point the module at the test DB and clear all rows."""
    models_module.DATABASE = TEST_DB
    models_module.init_db()
    conn = sqlite3.connect(TEST_DB)
    conn.execute("DELETE FROM product")
    conn.commit()
    conn.close()


######################################################################
# Base test class
######################################################################

class TestCaseBase(unittest.TestCase):
    def setUp(self):
        reset_db()


######################################################################
# Task 2 — Model Tests
######################################################################

class TestProductModel(TestCaseBase):
    """Unit tests for Product CRUD operations on the model layer."""

    # ── CREATE (baseline — other tests depend on this) ────────────────

    def test_create_a_product(self):
        """A new product is saved and gets an auto-generated id."""
        product = fake_product()
        self.assertIsNone(product.id)
        product.create()
        self.assertIsNotNone(product.id)

    def test_created_product_is_persisted(self):
        """The created product can be retrieved from the database."""
        product = fake_product(name="Rubber Duck")
        product.create()
        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Rubber Duck")

    # ── READ ──────────────────────────────────────────────────────────

    def test_read_a_product(self):
        """Read a product and check every field is returned correctly."""
        product = fake_product(
            name="Test Widget",
            description="A test widget description",
            price=Decimal("12.50"),
            available=True,
            category=Category.TOOLS,
        )
        product.create()

        found = Product.find(product.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id,          product.id)
        self.assertEqual(found.name,        "Test Widget")
        self.assertEqual(found.description, "A test widget description")
        self.assertEqual(found.price,       Decimal("12.50"))
        self.assertTrue(found.available)
        self.assertEqual(found.category,    Category.TOOLS)

    def test_read_product_not_found_returns_none(self):
        """Finding a non-existent id should return None."""
        result = Product.find(99999)
        self.assertIsNone(result)

    # ── UPDATE ────────────────────────────────────────────────────────

    def test_update_a_product(self):
        """Update all mutable fields and verify the changes are saved."""
        product = fake_product(name="Old Name", price=Decimal("5.00"))
        product.create()
        original_id = product.id

        product.name        = "New Name"
        product.description = "Updated description"
        product.price       = Decimal("99.99")
        product.available   = False
        product.category    = Category.FOOD
        product.update()

        updated = Product.find(original_id)
        self.assertEqual(updated.name,        "New Name")
        self.assertEqual(updated.description, "Updated description")
        self.assertEqual(updated.price,       Decimal("99.99"))
        self.assertFalse(updated.available)
        self.assertEqual(updated.category,    Category.FOOD)

    def test_update_without_id_raises_error(self):
        """Calling update() on a product with no id should raise DataValidationError."""
        product = fake_product()
        with self.assertRaises(DataValidationError):
            product.update()

    def test_update_does_not_create_duplicate(self):
        """update() must not insert a new row."""
        product = fake_product()
        product.create()
        product.name = "Changed"
        product.update()
        self.assertEqual(len(Product.all()), 1)

    # ── DELETE ────────────────────────────────────────────────────────

    def test_delete_a_product(self):
        """Deleting a product removes it from the database."""
        product = fake_product()
        product.create()
        pid = product.id

        product.delete()

        self.assertIsNone(Product.find(pid))

    def test_delete_only_removes_target_product(self):
        """Deleting one product must not affect others."""
        p1 = fake_product(name="Keep Me")
        p2 = fake_product(name="Delete Me")
        p1.create()
        p2.create()

        p2.delete()

        self.assertIsNotNone(Product.find(p1.id))
        self.assertIsNone(Product.find(p2.id))

    # ── LIST ALL ──────────────────────────────────────────────────────

    def test_list_all_products(self):
        """all() returns every product in the database."""
        for _ in range(5):
            fake_product().create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_list_all_returns_empty_list_when_no_products(self):
        """all() returns an empty list when the table is empty."""
        self.assertEqual(Product.all(), [])

    # ── FIND BY NAME ─────────────────────────────────────────────────

    def test_find_by_name(self):
        """find_by_name() returns only products with the matching name."""
        fake_product(name="Hammer").create()
        fake_product(name="Hammer").create()
        fake_product(name="Screwdriver").create()

        results = Product.find_by_name("Hammer")

        self.assertEqual(len(results), 2)
        for p in results:
            self.assertEqual(p.name, "Hammer")

    def test_find_by_name_no_match_returns_empty(self):
        """find_by_name() returns an empty list when there is no match."""
        fake_product(name="Drill").create()
        results = Product.find_by_name("Nonexistent")
        self.assertEqual(len(results), 0)

    def test_find_by_name_is_case_sensitive(self):
        """find_by_name() performs an exact, case-sensitive match."""
        fake_product(name="Hammer").create()
        self.assertEqual(len(Product.find_by_name("hammer")), 0)
        self.assertEqual(len(Product.find_by_name("Hammer")), 1)

    # ── FIND BY CATEGORY ─────────────────────────────────────────────

    def test_find_by_category(self):
        """find_by_category() returns only products in that category."""
        fake_product(category=Category.FOOD).create()
        fake_product(category=Category.FOOD).create()
        fake_product(category=Category.TOOLS).create()
        fake_product(category=Category.CLOTHS).create()

        results = Product.find_by_category(Category.FOOD)

        self.assertEqual(len(results), 2)
        for p in results:
            self.assertEqual(p.category, Category.FOOD)

    def test_find_by_category_no_match_returns_empty(self):
        """find_by_category() returns an empty list when no products match."""
        fake_product(category=Category.TOOLS).create()
        results = Product.find_by_category(Category.AUTOMOTIVE)
        self.assertEqual(len(results), 0)

    def test_find_by_each_category(self):
        """Verify find_by_category works for every Category enum value."""
        for cat in Category:
            reset_db()
            fake_product(category=cat).create()
            results = Product.find_by_category(cat)
            self.assertEqual(len(results), 1, f"Failed for category {cat.name}")

    # ── FIND BY AVAILABILITY ─────────────────────────────────────────

    def test_find_by_availability_true(self):
        """find_by_availability(True) returns only available products."""
        fake_product(available=True).create()
        fake_product(available=True).create()
        fake_product(available=False).create()

        results = Product.find_by_availability(True)

        self.assertEqual(len(results), 2)
        for p in results:
            self.assertTrue(p.available)

    def test_find_by_availability_false(self):
        """find_by_availability(False) returns only unavailable products."""
        fake_product(available=True).create()
        fake_product(available=False).create()

        results = Product.find_by_availability(False)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].available)

    def test_find_by_availability_default_is_true(self):
        """Default parameter for find_by_availability() is True."""
        fake_product(available=True).create()
        fake_product(available=False).create()

        results = Product.find_by_availability()  # default = True

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].available)

    # ── SERIALISE / DESERIALISE ───────────────────────────────────────

    def test_serialize(self):
        """serialize() returns a dict with all expected keys and types."""
        product = fake_product(
            name="Widget", price=Decimal("9.99"), category=Category.TOOLS
        )
        product.create()
        data = product.serialize()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"],     "Widget")
        self.assertEqual(data["category"], "TOOLS")
        self.assertIsInstance(data["price"], str)
        self.assertIn("id",          data)
        self.assertIn("description", data)
        self.assertIn("available",   data)

    def test_deserialize_a_product(self):
        """deserialize() populates all fields correctly."""
        data = {
            "name":        "Spanner",
            "description": "An adjustable spanner",
            "price":       "7.49",
            "available":   True,
            "category":    "TOOLS",
        }
        product = Product()
        product.deserialize(data)

        self.assertEqual(product.name,        "Spanner")
        self.assertEqual(product.description, "An adjustable spanner")
        self.assertEqual(product.price,       Decimal("7.49"))
        self.assertTrue(product.available)
        self.assertEqual(product.category,    Category.TOOLS)

    def test_deserialize_missing_key_raises_error(self):
        """deserialize() raises DataValidationError for missing required fields."""
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize({"name": "Incomplete"})

    def test_deserialize_invalid_available_raises_error(self):
        """deserialize() raises DataValidationError when 'available' is not bool."""
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize({
                "name": "Bad", "description": "Bad data",
                "price": "5.00", "available": "yes",   # must be True/False
                "category": "FOOD",
            })

    # ── REPR ─────────────────────────────────────────────────────────

    def test_repr(self):
        """__repr__ includes the product name."""
        product = fake_product(name="Widget")
        product.create()
        self.assertIn("Widget", repr(product))


######################################################################
# Entry point
######################################################################

if __name__ == "__main__":
    unittest.main(verbosity=2)
