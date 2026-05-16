#!/usr/bin/env python3
"""Verifica esistenza config.md per /competitor-deep-dive e ritorna stato JSON.

Usage: python scripts/discovery_check.py [--memory-path PATH]
Author: Filippo Greco / competitor-deep-dive 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        json.dumps(
            {
                "error": "PyYAML not installed. Run: pip install -r scripts/requirements.txt"
            }
        ),
        file=sys.stderr,
    )
    sys.exit(2)

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)


def parse_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        log.error(f"YAML parse error: {e}")
        return None


def parse_config_body(content: str) -> dict:
    """Best-effort parse of YAML in body (after frontmatter)."""
    if "---" in content:
        body = content.split("---", 2)[-1].strip()
    else:
        body = content
    try:
        return yaml.safe_load(body) or {}
    except yaml.YAMLError as e:
        log.error(f"Body YAML parse error: {e}")
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check /competitor-deep-dive config.md status"
    )
    parser.add_argument(
        "--memory-path",
        default=".claude/agents/competitor-deep-dive/memory/config.md",
        help="Path to config.md (default: project memory)",
    )
    args = parser.parse_args()

    config_path = Path(args.memory_path).expanduser()

    if not config_path.exists():
        result = {
            "exists": False,
            "path": str(config_path),
            "schema_version": None,
            "summary": None,
            "message": "Config not found. Run discovery (8 questions) to create.",
        }
        print(json.dumps(result, indent=2))
        return 0

    log.info(f"Reading {config_path}")
    content = config_path.read_text(encoding="utf-8")

    frontmatter = parse_frontmatter(content)
    body = parse_config_body(content)

    schema_version = (frontmatter or {}).get(
        "schema_version", body.get("schema_version")
    )

    competitors_analyzed = body.get("competitors_analyzed") or []

    summary = {
        "user_role": (body.get("user") or {}).get("role"),
        "industry": (body.get("business") or {}).get("industry"),
        "geo_target": (body.get("business") or {}).get("geo_target"),
        "gdpr_mode": (body.get("gdpr") or {}).get("mode_active"),
        "depth": (body.get("analysis") or {}).get("depth"),
        "output_format": (body.get("analysis") or {}).get("output_format"),
        "reviews_focus": (body.get("analysis") or {}).get("reviews_focus"),
        "baseline_tagline": ((body.get("business") or {}).get("baseline") or {}).get(
            "tagline"
        ),
        "competitors_analyzed_count": len(competitors_analyzed),
        "competitors_names": [
            c.get("name") for c in competitors_analyzed if isinstance(c, dict)
        ],
    }

    result = {
        "exists": True,
        "path": str(config_path),
        "schema_version": schema_version,
        "summary": summary,
        "frontmatter": frontmatter,
        "config": body,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
