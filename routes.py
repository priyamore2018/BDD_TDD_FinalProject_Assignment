"""
REST API Routes — Product Catalogue Microservice
Task 4: Read / Update / Delete / List All / List by Name /
        List by Category / List by Availability
"""
import logging
from flask import Flask, jsonify, request, abort

from service.models import Product, Category, DataValidationError, init_db

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask.app")

init_db()


######################################################################
# Health / Index
######################################################################

@app.route("/health", methods=["GET"])
def health():
    """Health-check endpoint."""
    return jsonify({"status": "OK"}), 200


@app.route("/", methods=["GET"])
def index():
    """Root — returns a simple welcome message."""
    return jsonify(
        name="Product Catalogue REST API Service",
        version="1.0",
        paths="/products",
    ), 200


######################################################################
# Task 4 — CRUD + Query Endpoints
######################################################################

# ── LIST ALL / LIST BY NAME / LIST BY CATEGORY / LIST BY AVAILABILITY ─

@app.route("/products", methods=["GET"])
def list_products():
    """
    GET /products
    Returns all products. Supports optional query-string filters:
      ?name=<str>
      ?category=<FOOD|CLOTHS|TOOLS|HOUSEWARES|AUTOMOTIVE|UNKNOWN>
      ?available=<true|false>
      ?price=<decimal>
    """
    logger.info("Request to list products")

    name      = request.args.get("name")
    category  = request.args.get("category")
    available = request.args.get("available")
    price     = request.args.get("price")

    # -- List by Name --------------------------------------------------
    if name:
        logger.info("Filtering by name: %s", name)
        products = Product.find_by_name(name)

    # -- List by Category ----------------------------------------------
    elif category:
        logger.info("Filtering by category: %s", category)
        try:
            cat_enum = getattr(Category, category.upper())
        except AttributeError:
            abort(
                400,
                description=(
                    f"Invalid category: '{category}'. "
                    "Valid values: FOOD, CLOTHS, TOOLS, HOUSEWARES, AUTOMOTIVE, UNKNOWN"
                ),
            )
        products = Product.find_by_category(cat_enum)

    # -- List by Availability ------------------------------------------
    elif available is not None:
        logger.info("Filtering by availability: %s", available)
        avail_bool = available.lower() in ("true", "1", "yes")
        products = Product.find_by_availability(avail_bool)

    # -- List by Price -------------------------------------------------
    elif price:
        logger.info("Filtering by price: %s", price)
        products = Product.find_by_price(price)

    # -- List All ------------------------------------------------------
    else:
        logger.info("Returning all products")
        products = Product.all()

    results = [p.serialize() for p in products]
    logger.info("Returning %d product(s)", len(results))
    return jsonify(results), 200


# ── CREATE ────────────────────────────────────────────────────────────

@app.route("/products", methods=["POST"])
def create_product():
    """
    POST /products
    Body (JSON):
    {
        "name":        "Hammer",
        "description": "16oz claw hammer",
        "price":       "14.99",
        "available":   true,
        "category":    "TOOLS"
    }
    """
    logger.info("Request to create a product")
    check_content_type("application/json")

    data    = request.get_json()
    product = Product()
    try:
        product.deserialize(data)
    except DataValidationError as err:
        abort(400, description=str(err))

    product.create()
    logger.info("Product with ID [%s] created.", product.id)

    location_url = f"/products/{product.id}"
    return jsonify(product.serialize()), 201, {"Location": location_url}


# ── READ ──────────────────────────────────────────────────────────────

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """GET /products/<id>  →  return a single product."""
    logger.info("Request to get product with id: %s", product_id)

    product = Product.find(product_id)
    if not product:
        abort(404, description=f"Product with id '{product_id}' was not found.")

    return jsonify(product.serialize()), 200


# ── UPDATE ────────────────────────────────────────────────────────────

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    PUT /products/<id>
    Send the full product object in the JSON body (same format as POST).
    """
    logger.info("Request to update product with id: %s", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(404, description=f"Product with id '{product_id}' was not found.")

    data = request.get_json()
    try:
        product.deserialize(data)
    except DataValidationError as err:
        abort(400, description=str(err))

    product.id = product_id
    product.update()

    logger.info("Product with ID [%s] updated.", product.id)
    return jsonify(product.serialize()), 200


# ── DELETE ────────────────────────────────────────────────────────────

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """DELETE /products/<id>  →  removes the product, returns 204 No Content."""
    logger.info("Request to delete product with id: %s", product_id)

    product = Product.find(product_id)
    if product:
        product.delete()
        logger.info("Product with ID [%s] deleted.", product_id)

    return "", 204


######################################################################
# Error Handlers
######################################################################

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e.description)), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e.description)), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(error="Method Not Allowed"), 405


@app.errorhandler(415)
def unsupported_media_type(e):
    return jsonify(error=str(e.description)), 415


######################################################################
# Helper
######################################################################

def check_content_type(media_type):
    """Abort with 415 if the Content-Type header is wrong."""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    abort(415, description=f"Content-Type must be {media_type}")


######################################################################
# Entry point
######################################################################

if __name__ == "__main__":
    print("=" * 60)
    print("  Product Catalogue API  →  http://127.0.0.1:5000")
    print("  Health check           →  http://127.0.0.1:5000/health")
    print("  Products               →  http://127.0.0.1:5000/products")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
