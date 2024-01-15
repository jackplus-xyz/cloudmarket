"""
# Author: Jack Huang
# GitHub username: jackplus-xyz
# Created:  11-19-2023
# Modified: 12-10-2023
# Description: Handles products endpoints
"""


from flask import Blueprint, jsonify, request
from google.cloud import datastore
import constants

PROJECT_ID = constants.project_id
USERS = constants.users
PRODUCTS = constants.products
ORDERS = constants.orders
LIMIT = constants.limit

MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
ALLOWED_KEYS = {"name", "description", "price", "stock"}

bp = Blueprint("product", __name__, url_prefix="/products")
client = datastore.Client(project=PROJECT_ID)


def is_valid_product(product):
    """Checks if the product object is a valid product."""
    return (
        len(product.get("name", "")) <= MAX_NAME_LENGTH
        and len(product.get("description", "")) <= MAX_DESCRIPTION_LENGTH
        and product.get("price", 0) >= 0
    )


@bp.route("", methods=["POST", "GET"])
def products_post_get():
    """
    POST: Create a new product
    GET: List all products on the marketplace
    """

    if request.method == "POST":
        if "application/json" not in request.accept_mimetypes:
            return (
                jsonify({"Error": "This endpoint only returns JSON data"}),
                406,
            )

        request_url = request.url
        content = request.get_json()

        # Check if the request is a list of products or a single product
        products = content if isinstance(content, list) else [content]
        new_products = []

        # Create a new product for each product in the request
        for product in products:
            if not is_valid_product(product) or not set(product.keys()) <= ALLOWED_KEYS:
                return (
                    jsonify(
                        {
                            "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
                        }
                    ),
                    400,
                )

            new_product = datastore.entity.Entity(key=client.key(PRODUCTS))
            new_product.update(
                {
                    "name": product["name"],
                    "description": product["description"],
                    "price": product["price"],
                    "stock": product["stock"] if "stock" in product else 0,
                    "orders": [],
                }
            )

            client.put(new_product)

            new_product["id"] = new_product.key.id
            new_product["self"] = request_url + "/" + str(new_product.key.id)
            new_products.append(new_product)

        # Return the new product(s)
        return (
            jsonify(new_products)
            if len(new_products) > 1
            else jsonify(new_products[0]),
            201,
        )

    elif request.method == "GET":
        if "application/json" not in request.accept_mimetypes:
            return (
                jsonify({"Error": "The request must accept JSON"}),
                406,
            )

        request_url = request.url

        # Get the total number of products
        query = client.query(kind=PRODUCTS)
        total_items = len(list(query.fetch()))

        # Get the products with pagination
        q_limit = int(request.args.get("limit", LIMIT))
        q_offset = int(request.args.get("offset", "0"))
        query = query.fetch(limit=q_limit, offset=q_offset)
        products = [
            {"id": product.key.id, "self": f"{request_url}/{product.key.id}", **product}
            for product in query
        ]

        results = {"products": products, "totalItems": total_items}

        # Add next link if there are more products
        if query.next_page_token:
            next_offset = q_offset + q_limit
            next_url = f"{request.base_url}?limit={q_limit}&offset={next_offset}"
            results["next"] = next_url

        return jsonify(results), 200


@bp.route("/<id>", methods=["GET", "PATCH", "PUT", "DELETE"])
def product_get_update_delete(id):
    if request.method == "GET":
        if "application/json" not in request.accept_mimetypes:
            return (
                jsonify({"Error": "This endpoint only returns JSON data"}),
                406,
            )

        key = client.key(PRODUCTS, int(id))
        product = client.get(key)

        if not product:
            return (
                jsonify({"Error": "No product with this product_id exists"}),
                404,
            )

        product["id"] = product.key.id
        product["self"] = request.url

        return jsonify(product), 200

    elif request.method == "PUT":
        if "application/json" not in request.accept_mimetypes:
            return (
                jsonify({"Error": "This endpoint only returns JSON data"}),
                406,
            )

        request_url = request.url
        content = request.get_json()
        product = client.get(client.key(PRODUCTS, int(id)))

        if not product:
            return (
                jsonify({"Error": "No product with this product_id exists"}),
                404,
            )

        # Verify that the request object is a valid product
        if not is_valid_product(content) or not set(content.keys()) == ALLOWED_KEYS:
            return (
                jsonify(
                    {
                        "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
                    }
                ),
                400,
            )

        product.update({key: content.get(key, product[key]) for key in ALLOWED_KEYS})
        client.put(product)

        # Update the product in all pending orders
        query = client.query(kind=ORDERS)
        query.add_filter("status", "=", "pending")
        orders = list(query.fetch())
        for order in orders:
            for order_product in order["products"]:
                if order_product["id"] == product.key.id:
                    order_product["name"] = product["name"]
                    order_product["description"] = product["description"]
                    order_product["price"] = product["price"]
                    client.put(order)

        query = client.query(kind=USERS)
        users = list(query.fetch())
        for user in users:
            for order in user["orders"]:
                if order["status"] == "pending":
                    for order_product in order["products"]:
                        if order_product["id"] == product.key.id:
                            order_product["name"] = product["name"]
                            order_product["description"] = product["description"]
                            order_product["price"] = product["price"]
                            client.put(user)

        product["id"] = product.key.id
        product["self"] = request_url

        return jsonify(product), 200

    elif request.method == "PATCH":
        if "application/json" not in request.accept_mimetypes:
            return (
                jsonify({"Error": "This endpoint only returns JSON data"}),
                406,
            )

        request_url = request.url
        content = request.get_json()
        product = client.get(client.key(PRODUCTS, int(id)))

        if not product:
            return (
                jsonify({"Error": "No product with this product_id exists"}),
                404,
            )

        if not is_valid_product(content) or not set(content.keys()) <= ALLOWED_KEYS:
            return (
                jsonify(
                    {
                        "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
                    }
                ),
                400,
            )

        product.update({key: content.get(key, product[key]) for key in ALLOWED_KEYS})
        client.put(product)

        # Update the product in all pending orders
        query = client.query(kind=ORDERS)
        query.add_filter("status", "=", "pending")
        orders = list(query.fetch())
        for order in orders:
            for order_product in order["products"]:
                if order_product["id"] == product.key.id:
                    order_product["name"] = product["name"]
                    order_product["description"] = product["description"]
                    order_product["price"] = product["price"]
                    client.put(order)

        query = client.query(kind=USERS)
        users = list(query.fetch())
        for user in users:
            for order in user["orders"]:
                if order["status"] == "pending":
                    for order_product in order["products"]:
                        if order_product["id"] == product.key.id:
                            order_product["name"] = product["name"]
                            order_product["description"] = product["description"]
                            order_product["price"] = product["price"]
                            client.put(user)

        client.put(product)

        product["id"] = product.key.id
        product["self"] = request_url

        return jsonify(product), 200

    elif request.method == "DELETE":
        key = client.key(PRODUCTS, int(id))
        product = client.get(key)
        if not product:
            return (
                jsonify({"Error": "No product with this product_id exists"}),
                404,
            )

        # Delete the product in all pending orders and users
        query = client.query(kind=ORDERS)
        query.add_filter("status", "=", "pending")
        orders = list(query.fetch())

        query = client.query(kind=USERS)
        users = list(query.fetch())
        for order in orders:
            for order_product in order["products"]:
                if order_product["id"] == product.key.id:
                    order["products"].remove(order_product)
                    client.put(order)

                    for user in users:
                        for user_order in user["orders"]:
                            if user_order["id"] == order.key.id:
                                user_order["products"].remove(order_product)
                                user_order["total"] -= (
                                    order_product["price"] * order_product["quantity"]
                                )
                                client.put(user)
                                break
                    break

        client.delete(key)

        return "", 204
