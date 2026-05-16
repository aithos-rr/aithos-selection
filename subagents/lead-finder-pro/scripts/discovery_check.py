#!/usr/bin/env python3
"""Verifica esistenza config.md per /lead-finder-pro e ritorna stato JSON.

Usage: python scripts/discovery_check.py [--memory-path PATH]
Author: Filippo Greco / lead-finder-pro 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import os
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
        description="Check /lead-finder-pro config.md status"
    )
    parser.add_argument(
        "--memory-path",
        default=".claude/agents/lead-finder-pro/memory/config.md",
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

    summary = {
        "user_role": (body.get("user") or {}).get("role"),
        "stack_enrichment": (body.get("stack") or {}).get("enrichment_primary"),
        "stack_crm": (body.get("stack") or {}).get("crm"),
        "icp_description": (body.get("icp") or {}).get("description"),
        "gdpr_mode": (body.get("gdpr") or {}).get("mode_active"),
        "monthly_volume": (body.get("preferences") or {}).get("monthly_volume"),
        "industry_pattern": (body.get("icp") or {}).get("industry_pattern"),
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
