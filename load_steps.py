"""
features/steps/load_steps.py
Task 5: Step definitions for loading BDD test data via the REST API.

These steps are shared across all feature files and populate the
database with known products before each scenario runs.
"""
import json
from behave import given
from decimal import Decimal


######################################################################
# Task 5 — Loading BDD Data
######################################################################

@given('the following products exist')
def step_load_products(context):
    """
    Load a table of products from the Behave scenario table.

    Example usage in a .feature file:
        Given the following products exist
          | name    | description     | price  | available | category |
          | Hammer  | A claw hammer   | 14.99  | True      | TOOLS    |
          | Bread   | White bread     | 1.99   | True      | FOOD     |

    Each row is POST-ed to the /products endpoint so the app processes
    them exactly as real API consumers would.
    """
    for row in context.table:
        # ── convert table strings to correct Python types ─────────────
        available = row["available"].strip().lower() in ("true", "1", "yes")

        payload = {
            "name":        row["name"],
            "description": row["description"],
            "price":       str(Decimal(row["price"])),
            "available":   available,
            "category":    row["category"].strip().upper(),
        }

        resp = context.client.post(
            "/products",
            json=payload,
            content_type="application/json",
        )

        assert resp.status_code == 201, (
            f"Failed to create product '{row['name']}': "
            f"HTTP {resp.status_code} — {resp.get_data(as_text=True)}"
        )


@given('the following product exists')
def step_load_single_product(context):
    """
    Load a single product from an inline table with one data row.
    Convenience alias for 'the following products exist'.
    """
    step_load_products(context)


@given('I have a product with id "{product_id:d}"')
def step_product_with_id(context, product_id):
    """
    Store the given product_id in the context for later use in steps
    that need to reference a specific product.
    """
    context.product_id = product_id


@given('there are no products in the database')
def step_no_products(context):
    """
    Confirm the database is empty (the environment wipes it before each
    scenario, so this is effectively a documentation step).
    """
    resp = context.client.get("/products")
    assert resp.status_code == 200
    products = resp.get_json()
    assert products == [], (
        f"Expected empty database but found {len(products)} product(s)"
    )


@given('I have created a product')
def step_create_default_product(context):
    """
    Quickly create a single product using default values and store the
    returned id in context.product_id for subsequent steps.
    """
    payload = {
        "name":        "Default Product",
        "description": "A default product for testing",
        "price":       "9.99",
        "available":   True,
        "category":    "UNKNOWN",
    }
    resp = context.client.post("/products", json=payload)
    assert resp.status_code == 201, f"Setup failed: {resp.status_code}"
    context.product_id = resp.get_json()["id"]
