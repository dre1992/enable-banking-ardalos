"""Shared Enable Banking API helpers — JWT auth, request session, error decoding."""
import time

import jwt
import requests

APPLICATION_ID = "db6b245a-5f09-4607-aa42-91d804991935"
PRIVATE_KEY_PATH = "/Users/andreasseficha/Downloads/db6b245a-5f09-4607-aa42-91d804991935.pem"
BASE_URL = "https://api.tilisy.com"


def make_jwt(ttl_seconds: int = 3600) -> str:
    with open(PRIVATE_KEY_PATH) as f:
        private_key = f.read()
    now = int(time.time())
    payload = {
        "iss": "enablebanking.com",
        "aud": "api.tilisy.com",
        "iat": now,
        "exp": now + ttl_seconds,
    }
    headers = {"typ": "JWT", "kid": APPLICATION_ID}
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {make_jwt()}"})
    return s


def check(r: requests.Response) -> dict:
    if not r.ok:
        try:
            body = r.json()
        except Exception:
            body = r.text
        raise RuntimeError(f"{r.status_code} {r.reason} on {r.url}\n{body}")
    return r.json()
