"""
# Author: Jack Huang
# GitHub username: jackplus-xyz
# Created:  11-19-2023
# Modified: 12-19-2023
# Description: A simple Flask app that implements a RESTful API
"""

import json
from functools import wraps
from os import environ as env
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen

import constants
import order
import product
import requests
import user
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from google.cloud import datastore
from jose import jwt
from werkzeug.exceptions import HTTPException
from verifyJWT import verify_jwt, AuthError

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CLIENT_ID = env.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env.get("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

USERS = constants.users
PRODUCTS = constants.products
ORDERS = constants.orders
DATA_MODEL = [USERS, PRODUCTS, ORDERS]
PROJECT_ID = constants.project_id
client = datastore.Client(project=PROJECT_ID)

app.register_blueprint(user.bp)
app.register_blueprint(product.bp)
app.register_blueprint(order.bp)

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
)


@app.route("/")
def index():
    if session.get("user"):
        user_info = session.get("user")["userinfo"]
        sub = user_info["sub"]

        # If the user is not in the datastore, add them
        user_key = client.key(USERS, sub)
        user = client.get(key=user_key)

        if not user:
            new_user = datastore.entity.Entity(key=client.key(USERS, sub))
            new_user.update(
                {
                    "name": user_info["name"],
                    "email": user_info["email"],
                }
            )

            client.put(new_user)
            user = new_user

        return render_template(
            "user-info.html",
            session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
            user_id=user.key.name,
            id_token=session["user"]["id_token"],
        )

    else:
        return render_template("welcome.html")


# Decode the JWT supplied in the Authorization header
@app.route("/decode", methods=["GET"])
def decode_jwt():
    payload = verify_jwt(request)
    return payload


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )
    elif request.method == "POST":
        content = request.get_json()
        username = content["username"]
        password = content["password"]
        body = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
        }
        headers = {"content-type": "application/json"}
        url = "https://" + AUTH0_DOMAIN + "/oauth/token"
        r = requests.post(url, json=body, headers=headers)

        if r.status_code != 200:
            return r.text, 401, {"Content-Type": "application/json"}

        return r.text, 200, {"Content-Type": "application/json"}


@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + AUTH0_DOMAIN
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        )
    )


@app.route("/cleanup", methods=["DELETE"])
def cleanup():
    for kind in [PRODUCTS, ORDERS]:
        query = client.query(kind=kind)
        results = list(query.fetch())
        for result in results:
            client.delete(result.key)

    query = client.query(kind=USERS)
    results = list(query.fetch())
    for result in results:
        result["orders"] = []
        client.put(result)

    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
