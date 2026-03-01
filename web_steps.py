"""
features/steps/web_steps.py
Task 7: Generic step definitions for interacting with the REST API
        and asserting on its responses.

These steps are reused across all feature scenarios.
"""
import json
from behave import when, then, given
from decimal import Decimal


######################################################################
# Task 7 — Step Definitions
######################################################################

# ── Request steps ─────────────────────────────────────────────────────

@when('I visit the "{url}" endpoint')
def step_visit_endpoint(context, url):
    """Send a GET request to the given URL and store the response."""
    context.resp = context.client.get(url)


@when('I send a GET request to "{url}"')
def step_send_get(context, url):
    context.resp = context.client.get(url)


@when('I send a POST request to "{url}" with body')
def step_send_post_with_body(context, url):
    """Send a POST request using the step's multiline text as JSON body."""
    payload = json.loads(context.text)
    context.resp = context.client.post(url, json=payload)


@when('I send a PUT request to "{url}" with body')
def step_send_put_with_body(context, url):
    """Send a PUT request using the step's multiline text as JSON body."""
    payload = json.loads(context.text)
    context.resp = context.client.put(url, json=payload)


@when('I send a DELETE request to "{url}"')
def step_send_delete(context, url):
    context.resp = context.client.delete(url)


@when('I delete the product with id "{product_id:d}"')
def step_delete_by_id(context, product_id):
    context.resp = context.client.delete(f"/products/{product_id}")


@when('I retrieve the product with id "{product_id:d}"')
def step_get_by_id(context, product_id):
    context.resp = context.client.get(f"/products/{product_id}")


@when('I update the product with id "{product_id:d}" with')
def step_update_by_id(context, product_id):
    """Send a PUT to /products/<id> with the Behave table as the body."""
    row     = context.table[0]
    payload = {
        "name":        row["name"],
        "description": row["description"],
        "price":       row["price"],
        "available":   row["available"].strip().lower() in ("true", "1", "yes"),
        "category":    row["category"].strip().upper(),
    }
    context.resp = context.client.put(f"/products/{product_id}", json=payload)


@when('I search for products by name "{name}"')
def step_search_by_name(context, name):
    context.resp = context.client.get(f"/products?name={name}")


@when('I search for products by category "{category}"')
def step_search_by_category(context, category):
    context.resp = context.client.get(f"/products?category={category.upper()}")


@when('I search for products by availability "{available}"')
def step_search_by_availability(context, available):
    context.resp = context.client.get(f"/products?available={available}")


@when('I list all products')
def step_list_all(context):
    context.resp = context.client.get("/products")


# ── Status code assertions ────────────────────────────────────────────

@then('the response status code should be "{status_code:d}"')
def step_check_status_code(context, status_code):
    assert context.resp.status_code == status_code, (
        f"Expected HTTP {status_code} but got {context.resp.status_code}\n"
        f"Body: {context.resp.get_data(as_text=True)}"
    )


@then('the response should be OK')
def step_response_ok(context):
    assert context.resp.status_code == 200, (
        f"Expected 200 OK but got {context.resp.status_code}"
    )


@then('the response should be Created')
def step_response_created(context):
    assert context.resp.status_code == 201, (
        f"Expected 201 Created but got {context.resp.status_code}"
    )


@then('the response should be No Content')
def step_response_no_content(context):
    assert context.resp.status_code == 204, (
        f"Expected 204 No Content but got {context.resp.status_code}"
    )


@then('the response should be Not Found')
def step_response_not_found(context):
    assert context.resp.status_code == 404, (
        f"Expected 404 Not Found but got {context.resp.status_code}"
    )


# ── Body / field assertions ───────────────────────────────────────────

@then('the response body should contain "{value}"')
def step_body_contains(context, value):
    body = context.resp.get_data(as_text=True)
    assert value in body, f"Expected '{value}' in response body but got:\n{body}"


@then('the response JSON field "{field}" should be "{value}"')
def step_json_field_equals_string(context, field, value):
    data = context.resp.get_json()
    assert str(data.get(field)) == value, (
        f"Expected {field}='{value}' but got '{data.get(field)}'"
    )


@then('the response JSON field "{field}" should be {value:d}')
def step_json_field_equals_int(context, field, value):
    data = context.resp.get_json()
    assert data.get(field) == value, (
        f"Expected {field}={value} but got '{data.get(field)}'"
    )


@then('the response JSON field "{field}" should be true')
def step_json_field_is_true(context, field):
    data = context.resp.get_json()
    assert data.get(field) is True, (
        f"Expected {field}=True but got '{data.get(field)}'"
    )


@then('the response JSON field "{field}" should be false')
def step_json_field_is_false(context, field):
    data = context.resp.get_json()
    assert data.get(field) is False, (
        f"Expected {field}=False but got '{data.get(field)}'"
    )


@then('the response list should have "{count:d}" item(s)')
def step_list_count(context, count):
    data = context.resp.get_json()
    assert isinstance(data, list), f"Expected a JSON list but got: {type(data)}"
    assert len(data) == count, f"Expected {count} item(s) but got {len(data)}"


@then('the response list should be empty')
def step_list_empty(context):
    data = context.resp.get_json()
    assert data == [], f"Expected empty list but got: {data}"


@then('every item in the list should have category "{category}"')
def step_every_item_has_category(context, category):
    data = context.resp.get_json()
    for item in data:
        assert item["category"] == category.upper(), (
            f"Expected category '{category.upper()}' but got '{item['category']}'"
        )


@then('every item in the list should have available "{available}"')
def step_every_item_has_availability(context, available):
    expected = available.strip().lower() in ("true", "1", "yes")
    data     = context.resp.get_json()
    for item in data:
        assert item["available"] == expected, (
            f"Expected available={expected} but got '{item['available']}'"
        )


@then('every item in the list should have name "{name}"')
def step_every_item_has_name(context, name):
    data = context.resp.get_json()
    for item in data:
        assert item["name"] == name, (
            f"Expected name='{name}' but got '{item['name']}'"
        )


@then('the product should no longer exist')
def step_product_gone(context):
    """Use the product_id stored in context to confirm deletion."""
    resp = context.client.get(f"/products/{context.product_id}")
    assert resp.status_code == 404, (
        f"Expected 404 after deletion but got {resp.status_code}"
    )


@then('I save the product id')
def step_save_product_id(context):
    """Save the id from the last response into context.product_id."""
    context.product_id = context.resp.get_json()["id"]
