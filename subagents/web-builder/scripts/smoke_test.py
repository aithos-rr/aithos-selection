#!/usr/bin/env python3
"""smoke_test.py — post-deploy HTTP 200 + response time check.

Tier B fallback (curl). Tier A usa Playwright MCP direttamente per screenshot.

Usage:
    python3 smoke_test.py <url>
    python3 smoke_test.py <url> --timeout 15 --paths "/,/dashboard,/api/health"

Output JSON:
    {
        "status": "ok" | "fail",
        "url": "...",
        "http_status": 200,
        "response_time_ms": 245,
        "paths_tested": [{"path": "/", "status": 200, "ms": 120}, ...],
        "errors": []
    }
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
import urllib.error


def check_url(url: str, timeout: float = 10.0) -> dict:
    """Single HTTP HEAD/GET check."""
    start = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "web-builder-smoke-test/1.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = int((time.time() - start) * 1000)
            return {
                "url": url,
                "status": resp.status,
                "ok": 200 <= resp.status < 400,
                "ms": elapsed_ms,
                "headers": dict(resp.headers.items()),
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "url": url,
            "status": e.code,
            "ok": False,
            "ms": elapsed_ms,
            "error": str(e),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {
            "url": url,
            "status": 0,
            "ok": False,
            "ms": int((time.time() - start) * 1000),
            "error": str(e),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Base URL to test (e.g., https://app.vercel.app)")
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="Per-request timeout (s)"
    )
    parser.add_argument(
        "--paths",
        default="/",
        help="Comma-separated paths to test (default: /)",
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    paths = [p.strip() for p in args.paths.split(",") if p.strip()]

    paths_tested: list[dict] = []
    errors: list[str] = []
    all_ok = True

    for path in paths:
        full_url = f"{base_url}{path}"
        result = check_url(full_url, timeout=args.timeout)
        paths_tested.append(
            {
                "path": path,
                "status": result["status"],
                "ms": result["ms"],
                "ok": result["ok"],
            }
        )
        if not result["ok"]:
            all_ok = False
            errors.append(f"{path}: HTTP {result['status']} {result.get('error', '')}")

    main_result = paths_tested[0] if paths_tested else {}

    output = {
        "status": "ok" if all_ok else "fail",
        "url": base_url,
        "http_status": main_result.get("status", 0),
        "response_time_ms": main_result.get("ms", 0),
        "paths_tested": paths_tested,
        "errors": errors,
    }

    print(json.dumps(output, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
