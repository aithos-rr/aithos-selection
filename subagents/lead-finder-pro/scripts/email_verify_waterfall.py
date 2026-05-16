#!/usr/bin/env python3
"""Verifica email waterfall multi-tier: Hunter (V2) -> Apollo (match) -> manual SMTP.

Soglia confidence default 0.80. Detect catch-all/role-based/disposable.
Cache result 30 giorni in <memory>/email_verify_cache/<hash>.json.

Usage:
  python scripts/email_verify_waterfall.py --email mario@acme.com
  python scripts/email_verify_waterfall.py --input-csv leads.csv --threshold 0.80

Author: Filippo Greco / lead-finder-pro 2026
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests not installed"}), file=sys.stderr)
    sys.exit(2)

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
ROLE_PREFIXES = {
    "info",
    "sales",
    "support",
    "admin",
    "noreply",
    "no-reply",
    "team",
    "hello",
    "contact",
}
DISPOSABLE_DOMAINS = {
    "tempmail.org",
    "mailinator.com",
    "10minutemail.com",
    "guerrillamail.com",
}
CACHE_DAYS = 30


def is_role_based(email: str) -> bool:
    local = email.split("@", 1)[0].lower()
    return local in ROLE_PREFIXES


def is_disposable(email: str) -> bool:
    domain = email.split("@", 1)[1].lower()
    return domain in DISPOSABLE_DOMAINS


def cache_key(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()[:16]


def cache_get(email: str, cache_dir: Path) -> dict | None:
    if not cache_dir.exists():
        return None
    f = cache_dir / f"{cache_key(email)}.json"
    if not f.exists():
        return None
    data = json.loads(f.read_text())
    age_days = (time.time() - data.get("verified_at_epoch", 0)) / 86400
    if age_days > CACHE_DAYS:
        return None
    return data


def cache_set(email: str, result: dict, cache_dir: Path) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    result_with_epoch = {**result, "verified_at_epoch": time.time()}
    (cache_dir / f"{cache_key(email)}.json").write_text(
        json.dumps(result_with_epoch, indent=2)
    )


def hunter_verify(email: str, api_key: str) -> dict:
    url = "https://api.hunter.io/v2/email-verifier"
    params = {"email": email, "api_key": api_key}
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=20)
        except requests.RequestException as e:
            log.warning(f"Hunter network error: {e}")
            time.sleep(2**attempt)
            continue
        if resp.status_code == 429:
            time.sleep(60)
            continue
        if resp.status_code >= 500:
            time.sleep(2**attempt)
            continue
        if resp.status_code == 451:
            return {"status": "opted_out_451", "score": 0, "result": "undeliverable"}
        resp.raise_for_status()
        return resp.json().get("data", {})
    raise RuntimeError("Hunter API failed after 3 retries")


def apollo_verify(email: str, api_key: str) -> dict:
    url = "https://api.apollo.io/v1/people/match"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    payload = {
        "email": email,
        "reveal_personal_emails": False,
        "reveal_phone_number": False,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
    except requests.RequestException as e:
        log.warning(f"Apollo network error: {e}")
        return {}
    if resp.status_code != 200:
        log.warning(f"Apollo {resp.status_code}: {resp.text[:200]}")
        return {}
    person = resp.json().get("person") or {}
    return {
        "verified": person.get("email_status") == "verified",
        "person": person,
    }


def manual_smtp_check(email: str) -> dict:
    """Best-effort manual SMTP check via smtplib. Often blocked. Use as last resort."""
    import smtplib
    import socket

    try:
        domain = email.split("@", 1)[1]
    except IndexError:
        return {"verified": False, "method": "smtp", "notes": "invalid format"}

    try:
        socket.setdefaulttimeout(10)
        with smtplib.SMTP(domain, 25) as smtp:
            smtp.helo()
            smtp.mail("verify@example.com")
            code, _ = smtp.rcpt(email)
            return {
                "verified": code == 250,
                "method": "smtp",
                "notes": f"smtp_code_{code}",
            }
    except Exception as e:
        log.warning(f"SMTP check failed: {e}")
        return {
            "verified": False,
            "method": "smtp",
            "notes": f"smtp_error_{type(e).__name__}",
        }


def verify_email(
    email: str,
    threshold: float,
    hunter_key: str | None,
    apollo_key: str | None,
    enable_smtp: bool,
    cache_dir: Path,
) -> dict:
    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        return {
            "email": email,
            "verified": False,
            "confidence": 0.0,
            "method": "regex",
            "flags": ["invalid_syntax"],
        }

    if is_disposable(email):
        return {
            "email": email,
            "verified": False,
            "confidence": 0.0,
            "method": "blocklist",
            "flags": ["disposable"],
        }

    cached = cache_get(email, cache_dir)
    if cached:
        log.info(f"Cache hit: {email}")
        return cached

    result = {
        "email": email,
        "verified": False,
        "confidence": 0.0,
        "method": None,
        "flags": [],
        "tier_used": None,
    }

    if is_role_based(email):
        result["flags"].append("role_based")

    if hunter_key:
        try:
            hunter_data = hunter_verify(email, hunter_key)
            score = (hunter_data.get("score") or 0) / 100.0
            status = hunter_data.get("status") or "unknown"
            result["raw_hunter"] = hunter_data
            result["method"] = "hunter"
            result["tier_used"] = 1
            result["confidence"] = score

            if status == "valid" and score >= threshold:
                result["verified"] = True
            elif status == "accept_all":
                result["flags"].append("catch_all")
                if score >= threshold:
                    result["verified"] = True
                    result["flags"].append("catch_all_warning")
            elif status == "webmail":
                result["flags"].append("webmail_warning")
                if score >= threshold:
                    result["verified"] = True
            elif status == "disposable":
                result["flags"].append("disposable")
            elif status == "opted_out_451":
                result["flags"].append("opt_out_hunter_451")

            if hunter_data.get("role"):
                if "role_based" not in result["flags"]:
                    result["flags"].append("role_based")

            if result["verified"] or status in (
                "invalid",
                "disposable",
                "opted_out_451",
            ):
                cache_set(email, result, cache_dir)
                return result
        except Exception as e:
            log.error(f"Hunter error for {email}: {e}")

    if apollo_key and not result["verified"]:
        log.info(f"Tier 2 Apollo: {email}")
        apollo_data = apollo_verify(email, apollo_key)
        if apollo_data.get("verified"):
            result["verified"] = True
            result["method"] = "apollo"
            result["tier_used"] = 2
            result["confidence"] = max(result["confidence"], 0.7)
            result["raw_apollo"] = apollo_data
            cache_set(email, result, cache_dir)
            return result

    if enable_smtp and not result["verified"]:
        log.info(f"Tier 3 SMTP: {email}")
        smtp_data = manual_smtp_check(email)
        if smtp_data["verified"]:
            result["verified"] = True
            result["method"] = "smtp"
            result["tier_used"] = 3
            result["confidence"] = max(result["confidence"], 0.6)
        result["raw_smtp"] = smtp_data

    cache_set(email, result, cache_dir)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Email verification waterfall multi-tier"
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--email", help="Single email to verify")
    src.add_argument("--input-csv", help="CSV with column 'email'")
    parser.add_argument(
        "--threshold", type=float, default=0.80, help="Min confidence (default 0.80)"
    )
    parser.add_argument("--hunter-key", default=os.environ.get("HUNTER_API_KEY"))
    parser.add_argument("--apollo-key", default=os.environ.get("APOLLO_API_KEY"))
    parser.add_argument(
        "--enable-smtp", action="store_true", help="Enable manual SMTP fallback"
    )
    parser.add_argument(
        "--cache-dir",
        default=".claude/agents/lead-finder-pro/memory/email_verify_cache",
    )
    args = parser.parse_args()

    if not args.hunter_key and not args.apollo_key and not args.enable_smtp:
        print(
            json.dumps(
                {
                    "error": "No verifier configured. Set HUNTER_API_KEY or APOLLO_API_KEY or --enable-smtp"
                }
            ),
            file=sys.stderr,
        )
        return 2

    cache_dir = Path(args.cache_dir).expanduser()
    results = []

    if args.email:
        emails = [args.email]
    else:
        with open(args.input_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "email" not in reader.fieldnames:
                print(
                    json.dumps({"error": "CSV missing 'email' column"}), file=sys.stderr
                )
                return 2
            emails = [row["email"] for row in reader if row.get("email")]

    for email in emails:
        r = verify_email(
            email,
            args.threshold,
            args.hunter_key,
            args.apollo_key,
            args.enable_smtp,
            cache_dir,
        )
        results.append(r)

    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
