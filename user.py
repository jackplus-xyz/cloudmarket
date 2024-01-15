"""
# Author: Jack Huang
# GitHub username: jackplus-xyz
# Created:  11-19-2023
# Modified: 12-19-2023
# Description: Handles users endpoints
"""

import json

import constants
from flask import Blueprint, Flask, jsonify, request
from google.cloud import datastore

PROJECT_ID = constants.project_id
USERS = constants.users
LIMIT = constants.limit

bp = Blueprint("user", __name__, url_prefix="/users")
client = datastore.Client(project=PROJECT_ID)


@bp.route("", methods=["GET"])
def users_get():
    """
    Return a list of all users
    """
    request_url = request.url
    query = client.query(kind=USERS)
    q_limit = int(request.args.get("limit", LIMIT))
    q_offset = int(request.args.get("offset", "0"))
    l_iterator = query.fetch(limit=q_limit, offset=q_offset)
    pages = l_iterator.pages
    users = list(next(pages))

    for user in users:
        user["id"] = user.key.name
        user["self"] = request_url + "/" + str(user.key.name)

    results = {"users": users}
    results["totalItems"] = len(users)

    if l_iterator.next_page_token:
        next_offset = q_offset + q_limit
        next_url = (
            request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        )
        results["next"] = next_url

    return jsonify(results), 200
