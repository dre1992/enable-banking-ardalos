"""
reconcile.py — Monthly transaction fetch using the session created by auth.py.

Reads session.json, fetches the last DAYS days of transactions from every
linked account, and writes transactions_YYYY-MM-DD.json.

Re-run auth.py if the session has expired (warns when <14 days remain).
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from eb_common import BASE_URL, make_session, check

SESSION_FILE = Path(__file__).parent / "session.json"
DAYS = 35  # cover a full month with margin around month-end runs
EXPIRY_WARN_DAYS = 14


def fetch_account_txs(s, uid: str, date_from: str) -> list[dict]:
    txs: list[dict] = []
    cursor = None
    while True:
        params = {"date_from": date_from}
        if cursor:
            params["continuation_key"] = cursor
        page = check(s.get(f"{BASE_URL}/accounts/{uid}/transactions", params=params))
        txs.extend(page.get("transactions", []))
        cursor = page.get("continuation_key")
        if not cursor:
            break
    return txs


def main() -> None:
    if not SESSION_FILE.exists():
        raise SystemExit(f"{SESSION_FILE.name} not found. Run auth.py first.")

    saved = json.loads(SESSION_FILE.read_text())
    valid_until = datetime.fromisoformat(saved["valid_until"])
    days_left = (valid_until - datetime.now(timezone.utc)).days

    if days_left < 0:
        raise SystemExit(
            f"Session expired on {valid_until.date()}. Re-run auth.py to re-authorize."
        )
    if days_left < EXPIRY_WARN_DAYS:
        print(f"⚠️  Session expires in {days_left} days — re-run auth.py soon.\n")

    s = make_session()
    date_from = (datetime.now(timezone.utc) - timedelta(days=DAYS)).strftime("%Y-%m-%d")
    print(f"Fetching transactions since {date_from} for {len(saved['accounts'])} accounts...\n")

    out: dict = {}
    for acc in saved["accounts"]:
        label = acc.get("iban") or acc["uid"]
        try:
            txs = fetch_account_txs(s, acc["uid"], date_from)
        except RuntimeError as e:
            print(f"  ✗ {label}: {e}")
            continue
        print(f"  ✓ {label} ({acc.get('type') or 'unknown'}) — {len(txs)} transactions")
        out[acc["uid"]] = {"account": acc, "transactions": txs}

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = Path(f"transactions_{stamp}.json")
    out_path.write_text(json.dumps(out, indent=2, default=str))
    total = sum(len(v["transactions"]) for v in out.values())
    print(f"\n✓ Wrote {out_path}  ({total} total transactions)")


if __name__ == "__main__":
    main()
