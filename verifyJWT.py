"""
# Author: Jack Huang
# GitHub username: jackplus-xyz
# Created:  11-21-2023
# Modified: 12-09-2023
# Description: Verify the JWT
"""

import json
from os import environ as env
from urllib.request import urlopen

from dotenv import find_dotenv, load_dotenv
from jose import jwt

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CLIENT_ID = env.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env.get("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")

ALGORITHMS = ["RS256"]


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def verify_jwt(request):
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"].split()
        token = auth_header[1]
    else:
        raise AuthError(
            {
                "code": "no auth header",
                "description": "Authorization header is missing",
            },
            401,
        )

    jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Invalid header. "
                "Use an RS256 signed JWT Access Token",
            },
            401,
        )

    if unverified_header["alg"] == "HS256":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Invalid header. "
                "Use an RS256 signed JWT Access Token",
            },
            401,
        )

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_CLIENT_ID,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )
        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "token is expired"}, 401
            )
        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    "code": "invalid_claims",
                    "description": "incorrect claims,"
                    " please check the audience and issuer",
                },
                401,
            )
        except Exception:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication" " token.",
                },
                401,
            )

        return payload
    else:
        raise AuthError(
            {"code": "no_rsa_key", "description": "No RSA key in JWKS"}, 401
        )
