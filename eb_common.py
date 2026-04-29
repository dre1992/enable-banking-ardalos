"""Shared Enable Banking API helpers — JWT auth, request session, error decoding."""
import os
import time
from pathlib import Path

import jwt
import requests

APPLICATION_ID = os.environ.get("ENABLE_BANKING_APPLICATION_ID", "db6b245a-5f09-4607-aa42-91d804991935")
PRIVATE_KEY_PATH = Path(os.environ.get(
    "ENABLE_BANKING_PRIVATE_KEY_PATH",
    "~/.config/enable-banking-ardalos/private_key.pem",
)).expanduser()
BASE_URL = os.environ.get("ENABLE_BANKING_BASE_URL", "https://api.tilisy.com")
SESSION_FILE = Path(os.environ.get(
    "ENABLE_BANKING_SESSION_FILE",
    "~/.local/state/enable-banking-ardalos/session.json",
)).expanduser()


def make_jwt(ttl_seconds: int = 3600) -> str:
    if not PRIVATE_KEY_PATH.exists():
        raise FileNotFoundError(
            f"Enable Banking private key not found: {PRIVATE_KEY_PATH}. "
            "Set ENABLE_BANKING_PRIVATE_KEY_PATH or copy it to the default secure path."
        )
    private_key = PRIVATE_KEY_PATH.read_text()
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
