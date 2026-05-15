#!/usr/bin/env python3
"""Wrapper Playwright (o curl fallback) per scrape homepage/about/product/pricing.

Usage: python scripts/positioning_extract.py --domain make.com [--pages homepage,about,product,pricing] [--output output/scrape.json]
Author: Filippo Greco / competitor-deep-dive 2026

Note: questo script genera un PIANO di scrape che il subagent esegue via MCP Playwright.
NON esegue Playwright direttamente (Playwright è MCP-side, non Python lib).
Output: JSON con liste URL da scrape + rate-limit defaults.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

DEFAULT_RATE_LIMIT_SECONDS = 2

PAGE_PATHS = {
    "homepage": ["", "/"],
    "about": ["/about", "/about-us", "/company", "/team"],
    "product": ["/product", "/features", "/platform", "/solutions"],
    "pricing": ["/pricing", "/plans", "/buy"],
}


def normalize_url(domain: str) -> str:
    """Ensure scheme present, normalize trailing slash."""
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    parsed = urlparse(domain)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base


def detect_stealth(domain_url: str, timeout: int = 10) -> dict:
    """Quick HEAD check homepage — detect 404 / coming-soon / DNS fail."""
    try:
        req = urllib.request.Request(domain_url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            content_length = int(resp.headers.get("Content-Length", "0"))
            if status >= 400:
                return {
                    "stealth_detected": True,
                    "reason": f"HTTP {status}",
                    "scrape_skip": True,
                }
            if 200 <= status < 300 and 0 < content_length < 500:
                return {
                    "stealth_detected": True,
                    "reason": f"content too small ({content_length} bytes — coming soon?)",
                    "scrape_skip": False,  # still scrape, flag
                }
            return {"stealth_detected": False, "status": status}
    except urllib.error.URLError as e:
        return {
            "stealth_detected": True,
            "reason": f"URL error: {e.reason}",
            "scrape_skip": True,
        }
    except Exception as e:
        return {
            "stealth_detected": True,
            "reason": f"error: {e}",
            "scrape_skip": True,
        }


def build_scrape_plan(domain_url: str, pages: list[str]) -> list[dict]:
    """Build list of URLs + Playwright actions."""
    plan = []
    for page_type in pages:
        if page_type not in PAGE_PATHS:
            log.warning(f"Unknown page type: {page_type}, skipping")
            continue
        # Try first path, the agent will fallback to others if 404
        candidate_paths = PAGE_PATHS[page_type]
        primary_url = (
            urljoin(domain_url, candidate_paths[0])
            if candidate_paths[0]
            else domain_url
        )
        plan.append(
            {
                "page_type": page_type,
                "primary_url": primary_url,
                "fallback_paths": candidate_paths[1:]
                if len(candidate_paths) > 1
                else [],
                "actions": [
                    {"action": "browser_navigate", "params": {"url": primary_url}},
                    {"action": "browser_wait_for", "params": {"time": 1.5}},
                    {
                        "action": "browser_evaluate",
                        "params": {"function": "() => document.body.innerText"},
                    },
                    {
                        "action": "browser_evaluate",
                        "params": {
                            "function": "() => Array.from(document.querySelectorAll('h1,h2,h3,p,a.cta,button')).slice(0,30).map(el => ({tag:el.tagName,text:el.innerText,href:el.href}))"
                        },
                    },
                ],
            }
        )
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build positioning scrape plan per /competitor-deep-dive"
    )
    parser.add_argument(
        "--domain", required=True, help="Competitor domain (e.g. make.com)"
    )
    parser.add_argument(
        "--pages",
        default="homepage,about,product,pricing",
        help="Pages to scrape (csv, default: homepage,about,product,pricing)",
    )
    parser.add_argument(
        "--rate-limit-seconds",
        type=int,
        default=DEFAULT_RATE_LIMIT_SECONDS,
        help="Min delay between requests same domain (default: 2)",
    )
    parser.add_argument("--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    domain_url = normalize_url(args.domain)
    pages = [p.strip() for p in args.pages.split(",") if p.strip()]

    stealth_info = detect_stealth(domain_url)
    if stealth_info.get("scrape_skip"):
        result = {
            "competitor_domain": args.domain,
            "domain_url": domain_url,
            "stealth_detected": True,
            "reason": stealth_info["reason"],
            "scrape_plan": [],
            "fallback_suggestion": "Schedule re-analysis after 30gg, or check spelling",
        }
    else:
        plan = build_scrape_plan(domain_url, pages)
        result = {
            "competitor_domain": args.domain,
            "domain_url": domain_url,
            "stealth_detected": stealth_info.get("stealth_detected", False),
            "stealth_reason": stealth_info.get("reason"),
            "rate_limit_seconds": args.rate_limit_seconds,
            "scrape_plan": plan,
            "scraper_preferred": "playwright_mcp",
            "fallback_chain": ["bash_curl_html_parse"],
        }

    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        log.info(f"Plan written to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
