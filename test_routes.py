"""
tests/test_routes.py
Task 3: Integration tests for the REST API routes.

Covers: Read / Update / Delete / List All / List by Name /
        List by Category / List by Availability
"""
import os
import sys
import tempfile
import sqlite3
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import service.models as models_module
from service.models import Product, Category
from tests.factories import ProductFactory, fake_product

# ── shared temp database ─────────────────────────────────────────────
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
TEST_DB = _tmp.name


def reset_db():
    models_module.DATABASE = TEST_DB
    models_module.init_db()
    conn = sqlite3.connect(TEST_DB)
    conn.execute("DELETE FROM product")
    conn.commit()
    conn.close()


def _seed(product: Product) -> Product:
    """Helper: persist a fake product and return it."""
    product.create()
    return product


######################################################################
# Base — set up Flask test client once for the whole class
######################################################################

class TestCaseBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        reset_db()
        from service.routes import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def setUp(self):
        reset_db()

    # ── convenience helpers ───────────────────────────────────────────

    def _post(self, **fields) -> dict:
        """POST a product to /products and return the JSON response body."""
        payload = {
            "name":        fields.get("name",        "Widget"),
            "description": fields.get("description", "A test product"),
            "price":       fields.get("price",       "9.99"),
            "available":   fields.get("available",   True),
            "category":    fields.get("category",    "TOOLS"),
        }
        resp = self.client.post("/products", json=payload)
        self.assertEqual(resp.status_code, 201)
        return resp.get_json()

    def _seed_many(self, count=3, **overrides) -> list:
        """Create *count* products via the API and return their JSON dicts."""
        return [self._post(**overrides) for _ in range(count)]


######################################################################
# Health / Index
######################################################################

class TestHealthIndex(TestCaseBase):

    def test_health_returns_200(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "OK")

    def test_index_returns_200(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)


######################################################################
# Task 3 — Route Tests
######################################################################

class TestCreateProduct(TestCaseBase):

    def test_create_product_returns_201(self):
        resp = self.client.post("/products", json={
            "name": "Hammer", "description": "Claw hammer",
            "price": "14.99", "available": True, "category": "TOOLS",
        })
        self.assertEqual(resp.status_code, 201)

    def test_create_product_returns_correct_fields(self):
        data = self._post(name="Hammer", category="TOOLS")
        self.assertEqual(data["name"],     "Hammer")
        self.assertEqual(data["category"], "TOOLS")
        self.assertIn("id", data)

    def test_create_product_location_header(self):
        resp = self.client.post("/products", json={
            "name": "Wrench", "description": "Adjustable wrench",
            "price": "12.99", "available": True, "category": "TOOLS",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)

    def test_create_product_bad_content_type_returns_415(self):
        resp = self.client.post(
            "/products",
            data='{"name":"x"}',
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, 415)

    def test_create_product_missing_field_returns_400(self):
        resp = self.client.post("/products", json={"name": "Incomplete"})
        self.assertEqual(resp.status_code, 400)


# ── READ ──────────────────────────────────────────────────────────────

class TestReadProduct(TestCaseBase):

    def test_read_product_returns_200(self):
        """GET /products/<id> returns the product with status 200."""
        created = self._post(name="Drill")
        resp = self.client.get(f"/products/{created['id']}")
        self.assertEqual(resp.status_code, 200)

    def test_read_product_returns_correct_data(self):
        """The returned JSON matches what was created."""
        created = self._post(name="Drill", price="29.99", category="TOOLS")
        resp    = self.client.get(f"/products/{created['id']}")
        data    = resp.get_json()

        self.assertEqual(data["name"],     "Drill")
        self.assertEqual(data["price"],    "29.99")
        self.assertEqual(data["category"], "TOOLS")

    def test_read_product_not_found_returns_404(self):
        """GET /products/<non-existent-id> returns 404."""
        resp = self.client.get("/products/99999")
        self.assertEqual(resp.status_code, 404)

    def test_read_returns_all_expected_fields(self):
        """Response body includes all product fields."""
        created = self._post()
        data    = self.client.get(f"/products/{created['id']}").get_json()
        for field in ("id", "name", "description", "price", "available", "category"):
            self.assertIn(field, data, f"Missing field: {field}")


# ── UPDATE ────────────────────────────────────────────────────────────

class TestUpdateProduct(TestCaseBase):

    def test_update_product_returns_200(self):
        """PUT /products/<id> returns 200 on success."""
        pid  = self._post()["id"]
        resp = self.client.put(f"/products/{pid}", json={
            "name": "Updated", "description": "Updated desc",
            "price": "19.99", "available": False, "category": "FOOD",
        })
        self.assertEqual(resp.status_code, 200)

    def test_update_product_persists_changes(self):
        """After PUT, a subsequent GET reflects the new values."""
        pid = self._post(name="Old Name", price="5.00")["id"]

        self.client.put(f"/products/{pid}", json={
            "name": "New Name", "description": "New desc",
            "price": "50.00", "available": False, "category": "FOOD",
        })

        data = self.client.get(f"/products/{pid}").get_json()
        self.assertEqual(data["name"],      "New Name")
        self.assertEqual(data["price"],     "50.00")
        self.assertEqual(data["category"],  "FOOD")
        self.assertFalse(data["available"])

    def test_update_nonexistent_product_returns_404(self):
        """PUT to a non-existent id returns 404."""
        resp = self.client.put("/products/99999", json={
            "name": "X", "description": "X", "price": "1.00",
            "available": True, "category": "TOOLS",
        })
        self.assertEqual(resp.status_code, 404)

    def test_update_bad_content_type_returns_415(self):
        pid = self._post()["id"]
        resp = self.client.put(
            f"/products/{pid}",
            data='{"name":"x"}',
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, 415)


# ── DELETE ────────────────────────────────────────────────────────────

class TestDeleteProduct(TestCaseBase):

    def test_delete_product_returns_204(self):
        """DELETE /products/<id> returns 204 No Content."""
        pid  = self._post()["id"]
        resp = self.client.delete(f"/products/{pid}")
        self.assertEqual(resp.status_code, 204)

    def test_deleted_product_is_gone(self):
        """After DELETE, a GET for the same id returns 404."""
        pid = self._post()["id"]
        self.client.delete(f"/products/{pid}")
        resp = self.client.get(f"/products/{pid}")
        self.assertEqual(resp.status_code, 404)

    def test_delete_nonexistent_product_still_returns_204(self):
        """DELETE on a non-existent id is idempotent and returns 204."""
        resp = self.client.delete("/products/99999")
        self.assertEqual(resp.status_code, 204)


# ── LIST ALL ──────────────────────────────────────────────────────────

class TestListAllProducts(TestCaseBase):

    def test_list_all_products_returns_200(self):
        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, 200)

    def test_list_all_returns_empty_list_initially(self):
        """GET /products on an empty database returns []."""
        data = self.client.get("/products").get_json()
        self.assertEqual(data, [])

    def test_list_all_returns_every_product(self):
        """GET /products returns all created products."""
        self._seed_many(4)
        data = self.client.get("/products").get_json()
        self.assertEqual(len(data), 4)

    def test_list_all_returns_list_type(self):
        self._post()
        data = self.client.get("/products").get_json()
        self.assertIsInstance(data, list)


# ── LIST BY NAME ─────────────────────────────────────────────────────

class TestListByName(TestCaseBase):

    def test_list_by_name_returns_matching_products(self):
        """GET /products?name=X returns only products with that name."""
        self._post(name="Hammer")
        self._post(name="Hammer")
        self._post(name="Drill")

        data = self.client.get("/products?name=Hammer").get_json()

        self.assertEqual(len(data), 2)
        for p in data:
            self.assertEqual(p["name"], "Hammer")

    def test_list_by_name_no_match_returns_empty(self):
        self._post(name="Drill")
        data = self.client.get("/products?name=Nonexistent").get_json()
        self.assertEqual(data, [])

    def test_list_by_name_returns_200(self):
        resp = self.client.get("/products?name=Anything")
        self.assertEqual(resp.status_code, 200)


# ── LIST BY CATEGORY ─────────────────────────────────────────────────

class TestListByCategory(TestCaseBase):

    def test_list_by_category_returns_matching_products(self):
        """GET /products?category=FOOD returns only FOOD products."""
        self._post(category="FOOD")
        self._post(category="FOOD")
        self._post(category="TOOLS")

        data = self.client.get("/products?category=FOOD").get_json()

        self.assertEqual(len(data), 2)
        for p in data:
            self.assertEqual(p["category"], "FOOD")

    def test_list_by_category_no_match_returns_empty(self):
        self._post(category="TOOLS")
        data = self.client.get("/products?category=AUTOMOTIVE").get_json()
        self.assertEqual(data, [])

    def test_list_by_category_invalid_returns_400(self):
        """GET /products?category=BOGUS returns 400 Bad Request."""
        resp = self.client.get("/products?category=BOGUS")
        self.assertEqual(resp.status_code, 400)

    def test_list_by_category_is_case_insensitive_in_query(self):
        """Query string category value should be uppercased by the route."""
        self._post(category="FOOD")
        data = self.client.get("/products?category=food").get_json()
        self.assertEqual(len(data), 1)

    def test_list_by_every_category(self):
        """Each category filter returns the correct subset."""
        for cat in Category:
            reset_db()
            self._post(category=cat.name)
            data = self.client.get(f"/products?category={cat.name}").get_json()
            self.assertEqual(len(data), 1, f"Failed for category {cat.name}")


# ── LIST BY AVAILABILITY ─────────────────────────────────────────────

class TestListByAvailability(TestCaseBase):

    def test_list_available_products(self):
        """GET /products?available=true returns only available products."""
        self._post(available=True)
        self._post(available=True)
        self._post(available=False)

        data = self.client.get("/products?available=true").get_json()

        self.assertEqual(len(data), 2)
        for p in data:
            self.assertTrue(p["available"])

    def test_list_unavailable_products(self):
        """GET /products?available=false returns only unavailable products."""
        self._post(available=True)
        self._post(available=False)

        data = self.client.get("/products?available=false").get_json()

        self.assertEqual(len(data), 1)
        self.assertFalse(data[0]["available"])

    def test_list_by_availability_returns_200(self):
        resp = self.client.get("/products?available=true")
        self.assertEqual(resp.status_code, 200)

    def test_availability_filter_accepts_1_and_0(self):
        """available=1 and available=0 are accepted as truthy/falsy."""
        self._post(available=True)
        self._post(available=False)

        self.assertEqual(len(self.client.get("/products?available=1").get_json()), 1)
        self.assertEqual(len(self.client.get("/products?available=0").get_json()), 1)


######################################################################
# Entry point
######################################################################

if __name__ == "__main__":
    unittest.main(verbosity=2)
