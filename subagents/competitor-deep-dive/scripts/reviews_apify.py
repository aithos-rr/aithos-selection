#!/usr/bin/env python3
"""Wrapper Apify actor per scrape reviews G2/Trustpilot/Capterra.

Usage: python scripts/reviews_apify.py --competitor "Make" --platforms "G2,Trustpilot" [--actor "zen-studio/software-review-scraper"] [--max-reviews 100] [--output output/reviews_make.json]
Author: Filippo Greco / competitor-deep-dive 2026

Note: questo script genera un PIANO di chiamata Apify che il subagent esegue via MCP `apify`.
NON esegue Apify direttamente (Apify è MCP-side). Output: JSON con actor input + fallback chain.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

PRIMARY_ACTOR = "zen-studio/software-review-scraper"

FALLBACK_CHAIN = [
    "focused_vanguard/multi-platform-reviews-scraper",
    "taroyamada/g2-capterra-review-intelligence",
    "scrapepilot/g2-software-reviews-scraper-ratings-pros-cons",
    "samstorm/g2-capterra-review-scraper",
]

DEPRECATED_ACTORS = ["lanky_quantifier/b2b-review-intelligence"]

RATE_LIMIT_DEFAULTS = {
    "G2": 5,
    "Trustpilot": 3,
    "Capterra": 5,
    "Gartner": 10,
    "TrustRadius": 5,
}

# Cost stimato per 1000 reviews (USD)
COST_PER_1000_REVIEWS = {
    "zen-studio/software-review-scraper": 3.99,
    "focused_vanguard/multi-platform-reviews-scraper": 5.0,
    "taroyamada/g2-capterra-review-intelligence": 4.0,
    "scrapepilot/g2-software-reviews-scraper-ratings-pros-cons": 3.0,
    "samstorm/g2-capterra-review-scraper": 4.0,
}


def build_actor_input(competitor: str, platforms: list[str], max_reviews: int) -> dict:
    """Build Apify actor input schema."""
    return {
        "query": competitor,
        "platforms": platforms,
        "maxResults": max_reviews,
        "includeProsAndCons": True,
        "sortBy": "most_recent",
        "language": "en",
    }


def estimate_cost(actor_id: str, n_platforms: int, max_reviews: int) -> float:
    """Stima costo USD per single competitor."""
    cost_per_k = COST_PER_1000_REVIEWS.get(actor_id, 5.0)
    total_reviews = n_platforms * max_reviews
    return round((total_reviews / 1000) * cost_per_k, 2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Apify reviews scrape plan per /competitor-deep-dive"
    )
    parser.add_argument("--competitor", required=True, help="Competitor name")
    parser.add_argument(
        "--platforms",
        default="G2,Trustpilot",
        help="Platform CSV (default: G2,Trustpilot)",
    )
    parser.add_argument(
        "--actor",
        default=PRIMARY_ACTOR,
        help=f"Apify actor ID (default: {PRIMARY_ACTOR})",
    )
    parser.add_argument(
        "--max-reviews",
        type=int,
        default=100,
        help="Max reviews per platform (default: 100)",
    )
    parser.add_argument(
        "--anonymize-pii",
        action="store_true",
        help="Apply GDPR EU mode anonymization (remove reviewer name/email/linkedin)",
    )
    parser.add_argument("--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    if args.actor in DEPRECATED_ACTORS:
        result = {
            "error": f"Actor {args.actor} is DEPRECATED",
            "fallback_chain": [PRIMARY_ACTOR] + FALLBACK_CHAIN,
        }
        print(json.dumps(result, indent=2), file=sys.stderr)
        return 2

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    invalid_platforms = [p for p in platforms if p not in RATE_LIMIT_DEFAULTS]
    if invalid_platforms:
        log.warning(f"Unknown platforms: {invalid_platforms} — using defaults")

    actor_input = build_actor_input(args.competitor, platforms, args.max_reviews)
    cost_estimate = estimate_cost(args.actor, len(platforms), args.max_reviews)

    plan = {
        "competitor": args.competitor,
        "platforms": platforms,
        "actor_primary": args.actor,
        "fallback_chain": [
            a for a in [PRIMARY_ACTOR] + FALLBACK_CHAIN if a != args.actor
        ],
        "actor_input": actor_input,
        "rate_limit_seconds": {p: RATE_LIMIT_DEFAULTS.get(p, 5) for p in platforms},
        "cost_estimate_usd": cost_estimate,
        "anonymize_pii_active": args.anonymize_pii,
        "anti_hallucination_enforce": True,
        "min_reviews_for_significance": 10,
        "post_2024_filter_recommended": True,
        "mcp_call_template": {
            "tool": "apify__call-actor",
            "args": {
                "actor_id": args.actor,
                "input": actor_input,
                "async": False,
            },
        },
        "apify_token_env": "APIFY_TOKEN",
        "apify_token_set": bool(os.environ.get("APIFY_TOKEN")),
    }

    output = json.dumps(plan, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        log.info(f"Plan written to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
