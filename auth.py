"""
auth.py — Enable Banking authorization / reauthorization.

Normal desktop flow:
  python auth.py

Phone/Telegram-friendly split flow:
  python auth.py --start-only
  # send/open the printed URL on phone, complete bank SCA, copy code from callback page
  python auth.py --code 'PASTE_CODE_HERE'

The resulting session is saved to the secure SESSION_FILE from eb_common.py.
"""
import argparse
import json
import uuid
import webbrowser
from datetime import datetime, timedelta, timezone

from eb_common import BASE_URL, SESSION_FILE, make_session, check

REDIRECT_URI = "https://dre1992.github.io/enable-banking-ardalos/callback/"
COUNTRY = "GR"
ASPSP_NAME = "Eurobank"
SESSION_DAYS = 180


def make_auth_request(s):
    valid_until = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    body = {
        "access": {"valid_until": valid_until},
        "aspsp": {"name": ASPSP_NAME, "country": COUNTRY},
        "state": str(uuid.uuid4()),
        "redirect_url": REDIRECT_URI,
        "psu_type": "business",
    }
    auth = check(s.post(f"{BASE_URL}/auth", json=body))
    return auth, valid_until


def save_session(sess: dict, valid_until: str) -> list[dict]:
    accounts = [
        {
            "uid": a["uid"],
            "iban": (a.get("account_id") or {}).get("iban"),
            "name": a.get("name"),
            "currency": a.get("currency"),
            "type": a.get("cash_account_type"),
            "product": a.get("product"),
        }
        for a in sess.get("accounts", [])
    ]

    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps({
        "session_id": sess["session_id"],
        "aspsp": ASPSP_NAME,
        "country": COUNTRY,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "valid_until": valid_until,
        "accounts": accounts,
    }, indent=2))
    SESSION_FILE.chmod(0o600)
    return accounts


def finish_with_code(s, code: str, valid_until: str | None = None) -> None:
    if not code:
        raise SystemExit("No code entered.")
    if valid_until is None:
        valid_until = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()

    sess = check(s.post(f"{BASE_URL}/sessions", json={"code": code.strip()}))
    accounts = save_session(sess, valid_until)
    print(f"\n✓ {len(accounts)} accounts linked. Session saved to {SESSION_FILE} (mode 600).")
    print(f"  Valid until {valid_until[:10]}. Run reconcile.py from now on.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-only", action="store_true", help="Print auth URL without opening browser or waiting for code")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser in desktop flow")
    parser.add_argument("--code", help="Finish auth with a code copied from the callback page")
    args = parser.parse_args()

    s = make_session()
    app = check(s.get(f"{BASE_URL}/application"))
    print(f"App: {app.get('name')!r}  active={app.get('active')}")

    if args.code:
        finish_with_code(s, args.code)
        return

    auth, valid_until = make_auth_request(s)
    print("\nAuthorization URL:")
    print(auth["url"])

    if args.start_only:
        print("\nSend/open this URL on your phone, complete Eurobank SCA, then paste the callback code back.")
        print("Finish locally with: python auth.py --code 'PASTE_CODE_HERE'")
        return

    if not args.no_open:
        webbrowser.open(auth["url"])

    print(f"\nAfter SCA, copy the code from {REDIRECT_URI}")
    code = input("Paste auth code: ").strip()
    finish_with_code(s, code, valid_until)


if __name__ == "__main__":
    main()
