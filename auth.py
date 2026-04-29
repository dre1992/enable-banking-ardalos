"""
auth.py — One-time bank authorization for Enable Banking.

Run this when:
  - First time setting up
  - The session in session.json has expired (PSD2 mandates re-auth every ~180 days)

It opens the bank's auth page in a browser, waits for you to paste the auth code
from the redirect callback page, then saves session details to session.json
which reconcile.py will reuse for monthly fetches.
"""
import json
import uuid
import webbrowser
from datetime import datetime, timedelta, timezone
from eb_common import BASE_URL, SESSION_FILE, make_session, check

REDIRECT_URI = "https://dre1992.github.io/enable-banking-ardalos/callback/"
COUNTRY = "GR"
ASPSP_NAME = "Eurobank"
SESSION_DAYS = 180


def main() -> None:
    s = make_session()

    app = check(s.get(f"{BASE_URL}/application"))
    print(f"App: {app.get('name')!r}  active={app.get('active')}")

    valid_until = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    body = {
        "access": {"valid_until": valid_until},
        "aspsp": {"name": ASPSP_NAME, "country": COUNTRY},
        "state": str(uuid.uuid4()),
        "redirect_url": REDIRECT_URI,
        "psu_type": "business",
    }
    auth = check(s.post(f"{BASE_URL}/auth", json=body))
    print(f"\nOpening browser:\n  {auth['url']}")
    webbrowser.open(auth["url"])

    print(f"\nAfter SCA, copy the code from {REDIRECT_URI}")
    code = input("Paste auth code: ").strip()
    if not code:
        raise SystemExit("No code entered.")

    sess = check(s.post(f"{BASE_URL}/sessions", json={"code": code}))

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

    print(f"\n✓ {len(accounts)} accounts linked. Session saved to {SESSION_FILE} (mode 600).")
    print(f"  Valid until {valid_until[:10]}.  Run reconcile.py from now on.")


if __name__ == "__main__":
    main()
