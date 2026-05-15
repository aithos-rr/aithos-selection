#!/usr/bin/env python3
"""Wrapper Apollo people-search / organization-search API V1.

Retry 3x exponential backoff su 429/5xx. API key via env APOLLO_API_KEY o --api-key.
NB: NON fidarti di email_status='verified' Apollo (bounce 15-25%) — passa sempre via email_verify_waterfall.py.

Usage:
  python scripts/apollo_search.py --query '{"person_titles":["VP Marketing"]}' --per-page 25
  python scripts/apollo_search.py --endpoint organizations --query '{"organization_locations":["Italy"]}'

Author: Filippo Greco / lead-finder-pro 2026
"""

import argparse
import json
import logging
import os
import sys
import time

try:
    import requests
except ImportError:
    print(
        json.dumps(
            {
                "error": "requests not installed. Run: pip install -r scripts/requirements.txt"
            }
        ),
        file=sys.stderr,
    )
    sys.exit(2)

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

ENDPOINTS = {
    "people": "https://api.apollo.io/v1/mixed_people/search",
    "organizations": "https://api.apollo.io/v1/organizations/search",
    "match": "https://api.apollo.io/v1/people/match",
    "bulk_match": "https://api.apollo.io/v1/people/bulk_match",
}


def apollo_call(
    endpoint_url: str, payload: dict, api_key: str, max_retries: int = 3
) -> dict:
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                endpoint_url, json=payload, headers=headers, timeout=30
            )
        except requests.RequestException as e:
            log.warning(f"Network error attempt {attempt + 1}: {e}")
            time.sleep(2**attempt)
            continue

        rate_remaining = resp.headers.get("X-RateLimit-Remaining", "n/a")
        log.info(f"Apollo {resp.status_code} | RateLimit-Remaining: {rate_remaining}")

        if resp.status_code == 429:
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - time.time(), 5)
            log.warning(f"Rate limit. Waiting {wait:.0f}s.")
            time.sleep(min(wait, 60))
            continue

        if resp.status_code >= 500:
            log.warning(f"Server error {resp.status_code}, backoff {2**attempt}s")
            time.sleep(2**attempt)
            continue

        if resp.status_code == 401:
            raise SystemExit("Apollo 401: invalid API key.")
        if resp.status_code == 422:
            log.error(f"422 invalid query: {resp.text}")
            raise SystemExit("Apollo 422: invalid query schema.")

        resp.raise_for_status()
        return resp.json()

    raise RuntimeError(f"Apollo API failed after {max_retries} retries")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apollo API wrapper")
    parser.add_argument(
        "--endpoint",
        choices=list(ENDPOINTS.keys()),
        default="people",
        help="Apollo endpoint (default: people)",
    )
    parser.add_argument("--query", required=True, help="JSON query string")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--per-page", type=int, default=25)
    parser.add_argument(
        "--api-key",
        default=os.environ.get("APOLLO_API_KEY"),
        help="API key (default: env APOLLO_API_KEY)",
    )
    parser.add_argument("--output", default="-", help="Output path (default: stdout)")
    args = parser.parse_args()

    if not args.api_key:
        print(
            json.dumps({"error": "Missing APOLLO_API_KEY env var or --api-key"}),
            file=sys.stderr,
        )
        return 2

    try:
        payload = json.loads(args.query)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid --query JSON: {e}"}), file=sys.stderr)
        return 2

    if args.endpoint in ("people", "organizations"):
        payload.setdefault("page", args.page)
        payload.setdefault("per_page", args.per_page)

    log.info(f"Calling {args.endpoint} with payload keys: {list(payload.keys())}")
    result = apollo_call(ENDPOINTS[args.endpoint], payload, args.api_key)

    output_text = json.dumps(result, indent=2, default=str)
    if args.output == "-":
        print(output_text)
    else:
        from pathlib import Path

        Path(args.output).write_text(output_text, encoding="utf-8")
        log.info(f"Output written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
