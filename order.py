"""
# Author: Jack Huang
# GitHub username: jackplus-xyz
# Created:  11-19-2023
# Modified: 12-23-2023
# Description: Handles orders endpoints
"""


import datetime
from flask import Blueprint, jsonify, request
from google.cloud import datastore
import constants
from verifyJWT import AuthError, verify_jwt


PROJECT_ID = constants.project_id
USERS = constants.users
PRODUCTS = constants.products
ORDERS = constants.orders
LIMIT = constants.limit

ALLOWED_KEYS = {"status", "billingAddress", "paymentMethod"}
STATUS_VALUES = {"pending", "completed", "canceled"}
PAYMENT_METHOD_VALUES = {"credit", "debit", "cash"}

bp = Blueprint("order", __name__, url_prefix="/orders")
client = datastore.Client(project=PROJECT_ID)


def is_valid_order(order):
    """Checks if the order object is a valid order."""
    if order.get("status"):
        if order.get("status") not in STATUS_VALUES:
            return False

    if order.get("paymentMethod"):
        if order.get("paymentMethod") not in PAYMENT_METHOD_VALUES:
            return False

    if not order.get("billingAddress"):
        return False

    return True


@bp.route("", methods=["POST", "GET"])
def orders_post_get():
    """
    POST: Create a new order
    GET: List all orders of the current user
    """

    if request.method == "POST":
        """
        Create a new order
        Only the current user can create an order for themselves

        """
        try:
            payload = verify_jwt(request)
            request_url_root = request.url_root

            if "application/json" not in request.accept_mimetypes:
                return (
                    jsonify({"Error": "The request must accept JSON "}),
                    406,
                )

            sub = payload["sub"]
            user_key = client.key(USERS, sub)
            user = client.get(user_key)

            if not user:
                return (
                    jsonify({"Error": "No user with this user_id exists"}),
                    404,
                )

            user["id"] = user.key.name
            user["self"] = request_url_root + "users/" + str(user.key.name)

            # Verify the content of the order
            content = request.get_json()
            if (
                not content
                or not set(content.keys()) <= ALLOWED_KEYS
                or not is_valid_order(content)
            ):
                return (
                    jsonify(
                        {
                            "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
                        }
                    ),
                    400,
                )

            # Create a new order with the user as the parent
            new_order_key = client.key(USERS, sub, ORDERS)
            new_order = datastore.Entity(key=new_order_key)
            new_order.update(
                {
                    "total": 0,
                    "status": content["status"] if "status" in content else "pending",
                    "billingAddress": content["billingAddress"],
                    "paymentMethod": content["paymentMethod"],
                    "dateCreated": datetime.datetime.now(),
                    "dateModified": datetime.datetime.now(),
                }
            )

            client.put(new_order)
            new_order["id"] = new_order.key.id
            new_order["self"] = request_url_root + "orders/" + str(new_order.key.id)

            return jsonify(new_order), 201

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )

    elif request.method == "GET":
        try:
            payload = verify_jwt(request)

            if "application/json" not in request.accept_mimetypes:
                return (
                    jsonify({"Error": "The request must accept JSON"}),
                    406,
                )

            request_url = request.url
            sub = payload["sub"]

            user_key = client.key(USERS, sub)
            query = client.query(kind=ORDERS, ancestor=user_key)
            total_items = len(list(query.fetch()))

            # Pagination
            q_limit = int(request.args.get("limit", LIMIT))
            q_offset = int(request.args.get("offset", "0"))
            query = query.fetch(limit=q_limit, offset=q_offset)
            orders = [
                {"id": order.key.id, "self": f"{request_url}/{order.key.id}", **order}
                for order in query
            ]

            results = {"orders": orders, "totalItems": total_items}

            if query.next_page_token:
                next_offset = q_offset + q_limit
                next_url = f"{request.base_url}?limit={q_limit}&offset={next_offset}"
                results["next"] = next_url

            return jsonify(results), 200

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )


@bp.route("/<id>", methods=["GET", "PATCH", "PUT", "DELETE"])
def order_get_update_delete(id):
    """
    GET: Get an order
    PATCH: Update an order partially
    PUT: Update an order completely
    DELETE: Delete an order
    """

    if request.method == "GET":
        try:
            payload = verify_jwt(request)
            sub = payload["sub"]
            request_url = request.url

            if "application/json" not in request.accept_mimetypes:
                return (
                    jsonify({"Error": "This endpoint only returns JSON data"}),
                    406,
                )

            user_key = client.key(USERS, sub)
            order_key = client.key(ORDERS, int(id), parent=user_key)
            order = client.get(order_key)

            if not order:
                return (
                    jsonify({"Error": "No order with this order_id exists"}),
                    404,
                )

            # TODOs: Get the products in the order
            products = order["products"]

            order["id"] = order.key.id
            order["self"] = request_url

            return jsonify(order), 200

        except Exception as e:
            if e == AuthError:
                return (
                    jsonify(e.error),
                    401,
                )
            else:
                return (
                    "Unknown error",
                    500,
                )

    elif request.method == "PUT":
        try:
            payload = verify_jwt(request)
            sub = payload["sub"]

            order = client.get(client.key(ORDERS, int(id)))

            if not order:
                return (
                    jsonify({"Error": "No order with this order_id exists"}),
                    404,
                )

            if order["user"] != sub:
                return (
                    jsonify({"Error": "You do not have access to this order"}),
                    403,
                )

            user = client.get(client.key(USERS, sub))
            user_orders = user["orders"]
            if not any(order.key.id == user_order.id for user_order in user_orders):
                return (
                    jsonify({"Error": "This order is not in this user's orders"}),
                    403,
                )

            content = request.get_json()
            if set(content.keys()) != ALLOWED_KEYS or not is_valid_order(content):
                return (
                    jsonify(
                        {
                            "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
                        }
                    ),
                    400,
                )

            order.update({key: content.get(key, order[key]) for key in ALLOWED_KEYS})
            order["dateModified"] = datetime.datetime.now()
            client.put(order)

            order_index = next(
                index
                for index, user_order in enumerate(user_orders)
                if user_order.id == order.key.id
            )
            if order_index is not None:
                user_orders[order_index] = order
            client.put(user)

            order["id"] = order.key.id
            order["self"] = request.url

            return jsonify(order), 200

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )

    elif request.method == "PATCH":
        try:
            payload = verify_jwt(request)
            sub = payload["sub"]

            order = client.get(client.key(ORDERS, int(id)))

            if not order:
                return (
                    jsonify({"Error": "No order with this order_id exists"}),
                    404,
                )

            if order["user"] != sub:
                return (
                    jsonify({"Error": "You do not have access to this order"}),
                    403,
                )

            user = client.get(client.key(USERS, sub))
            user_orders = user["orders"]
            if not any(order.key.id == user_order.id for user_order in user_orders):
                return (
                    jsonify({"Error": "This order is not in this user's orders"}),
                    403,
                )

            content = request.get_json()
            if not set(content.keys()) <= ALLOWED_KEYS or not is_valid_order(content):
                return (
                    jsonify(
                        {
                            "Error": "The request object is missing at least one of the required attributes or has invalid attributes"
                        }
                    ),
                    400,
                )

            order.update({key: content.get(key, order[key]) for key in ALLOWED_KEYS})
            order["dateModified"] = datetime.datetime.now()
            client.put(order)

            order_index = next(
                index
                for index, user_order in enumerate(user_orders)
                if user_order.id == order.key.id
            )
            if order_index is not None:
                user_orders[order_index] = order
            client.put(user)

            order["id"] = order.key.id
            order["self"] = request.url

            return jsonify(order), 200

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )

    elif request.method == "DELETE":
        try:
            payload = verify_jwt(request)
            sub = payload["sub"]

            key = client.key(ORDERS, int(id))
            order = client.get(key)

            if not order:
                return (
                    jsonify({"Error": "No order with this order_id exists"}),
                    404,
                )

            if order["user"] != sub:
                return (
                    jsonify({"Error": "You do not have access to this order"}),
                    403,
                )

            user = client.get(client.key(USERS, sub))
            order_index = next(
                index
                for index, user_order in enumerate(user["orders"])
                if user_order.id == order.key.id
            )
            user["orders"].pop(order_index)
            client.put(user)

            client.delete(key)
            return "", 204

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )


@bp.route("/<oid>/products/<pid>", methods=["PUT", "DELETE"])
def order_products_put_delete(oid, pid):
    """
    PUT: Add a product to an order
    DELETE: Remove a product from an order
    """

    if request.method == "PUT":
        try:
            payload = verify_jwt(request)
            sub = payload["sub"]

            if "application/json" not in request.accept_mimetypes:
                return (
                    jsonify({"Error": "This endpoint only returns JSON data"}),
                    406,
                )

            quantity = request.args.get("quantity", type=int)
            if not quantity or quantity <= 0:
                return (
                    jsonify({"Error": "The quantity must be a positive integer"}),
                    400,
                )

            order = client.get(client.key(ORDERS, int(oid)))

            if not order:
                return (
                    jsonify({"Error": "No order with this order_id exists"}),
                    404,
                )

            if order["user"] != sub:
                return (
                    jsonify({"Error": "You do not have access to this order"}),
                    403,
                )

            if order["status"] != "pending":
                return (
                    jsonify(
                        {"Error": "You cannot add products to a non-pending order"}
                    ),
                    403,
                )

            product = client.get(client.key(PRODUCTS, int(pid)))

            if not product:
                return (
                    jsonify({"Error": "No product with this product_id exists"}),
                    404,
                )

            if product["stock"] <= 0 or product["stock"] < quantity:
                return (
                    jsonify({"Error": "This product is out of stock"}),
                    403,
                )

            if order["products"] and product.key.id in [
                product.key.id for product in order["products"]
            ]:
                return (
                    jsonify({"Error": "This product is already in this order"}),
                    403,
                )

            # Update the product
            product["stock"] -= quantity
            product_order = {
                "id": order.key.id,
                "quantity": quantity,
            }
            product["orders"].append(product_order)
            client.put(product)

            product["quantity"] = quantity
            product["id"] = product.key.id
            product.pop("stock")

            order["products"].append(product)
            order["total"] += product["price"] * quantity
            order["dateModified"] = datetime.datetime.now()
            client.put(order)

            # Update the order in the user
            user = client.get(client.key(USERS, sub))
            user_orders = user["orders"]
            for user_order in user_orders:
                if user_order.id == order.key.id:
                    user_order["products"] = order["products"]
                    user_order["total"] = order["total"]
                    user_order["dateModified"] = order["dateModified"]
                    break

            client.put(user)

            return "", 204

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )

    elif request.method == "DELETE":
        try:
            payload = verify_jwt(request)
            sub = payload["sub"]

            if "application/json" not in request.accept_mimetypes:
                return (
                    jsonify({"Error": "This endpoint only returns JSON data"}),
                    406,
                )

            order = client.get(client.key(ORDERS, int(oid)))

            if not order:
                return (
                    jsonify({"Error": "No order with this order_id exists"}),
                    404,
                )

            if order["user"] != sub:
                return (
                    jsonify({"Error": "You do not have access to this order"}),
                    403,
                )

            if order["status"] != "pending":
                return (
                    jsonify(
                        {"Error": "You cannot add products to a non-pending order"}
                    ),
                    403,
                )

            product = client.get(client.key(PRODUCTS, int(pid)))

            if not product:
                return (
                    jsonify({"Error": "No product with this product_id exists"}),
                    404,
                )

            order_product_index = None

            if order["products"]:
                for index, order_product in enumerate(order["products"]):
                    if order_product["id"] == product.key.id:
                        order_product_index = index
                        break

            if order_product_index is None:
                return (
                    jsonify({"Error": "This product is not in this order"}),
                    403,
                )

            order_product = order["products"][order_product_index]
            quantity = order_product["quantity"]

            product["stock"] += quantity
            for index, product_order in enumerate(product["orders"]):
                if product_order["id"] == order.key.id:
                    product["orders"].pop(index)
                    break
            client.put(product)

            order["total"] -= product["price"] * quantity
            order["dateModified"] = datetime.datetime.now()
            order["products"].pop(order_product_index)
            client.put(order)

            user = client.get(client.key(USERS, sub))
            user_orders = user["orders"]
            for user_order in user_orders:
                if user_order.id == order.key.id:
                    user_order["products"] = order["products"]
                    user_order["total"] = order["total"]
                    user_order["dateModified"] = order["dateModified"]
                    client.put(user)
                    break

            return "", 204

        except Exception as e:
            return (
                jsonify(e.error),
                401,
            )
