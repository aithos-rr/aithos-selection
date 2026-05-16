#!/usr/bin/env python3
"""mcp_detect.py — Detect MCP availability per /seo-strategist session.

Probes ~/.claude.json e MCP user/local config to detect which MCP server are configured.
Output JSON {mcp_available: {...}, fallback_active: {...}}.

Usage:
    python3 mcp_detect.py
    python3 mcp_detect.py --output mcp.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


# MCP nomi attesi per /seo-strategist (vedi seo-strategist.md frontmatter mcpServers)
EXPECTED_MCPS = ["parallel-cli", "playwright", "apify", "google-personal", "context7"]

# Fallback chain per ogni MCP missing
FALLBACK_MAP = {
    "parallel-cli": "websearch+webfetch",
    "playwright": "bash+curl+readability_parser",
    "apify": "manual_user_export",
    "google-personal": "markdown_local",
    "context7": "webfetch_fallback",
}


def load_claude_config() -> dict:
    candidates = [
        Path.home() / ".claude.json",
        Path.home() / ".config" / "claude" / "claude.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:  # noqa: BLE001
                continue
    return {}


def load_local_settings() -> dict:
    candidates = [
        Path.cwd() / ".claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.local.json",
    ]
    merged = {}
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged.update(data)
            except Exception:  # noqa: BLE001
                continue
    return merged


def detect_mcp(config: dict) -> dict[str, bool]:
    """Return {mcp_name: present_bool}."""
    available = {name: False for name in EXPECTED_MCPS}

    # Search across known config keys
    mcp_servers = {}
    for key in ("mcpServers", "mcp_servers", "mcps"):
        if key in config and isinstance(config[key], dict):
            mcp_servers.update(config[key])

    # Walk per-project config too if present
    projects = config.get("projects") or {}
    for proj in projects.values() if isinstance(projects, dict) else []:
        if isinstance(proj, dict):
            for key in ("mcpServers", "mcp_servers", "mcps"):
                if key in proj and isinstance(proj[key], dict):
                    mcp_servers.update(proj[key])

    for name in EXPECTED_MCPS:
        if name in mcp_servers:
            available[name] = True

    return available


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect MCP availability for /seo-strategist"
    )
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    user_config = load_claude_config()
    local_config = load_local_settings()

    mcp_available = detect_mcp(user_config)
    # local config may override (rare)
    if local_config:
        local_avail = detect_mcp(local_config)
        for k, v in local_avail.items():
            if v:
                mcp_available[k] = True

    fallback_active = {
        name: FALLBACK_MAP.get(name, "manual")
        for name, present in mcp_available.items()
        if not present
    }

    result = {
        "mcp_available": mcp_available,
        "fallback_active": fallback_active,
        "summary": {
            "total_expected": len(EXPECTED_MCPS),
            "present": sum(1 for v in mcp_available.values() if v),
            "missing": sum(1 for v in mcp_available.values() if not v),
        },
        "expected_mcps": EXPECTED_MCPS,
    }

    output_str = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Wrote {args.output}")
    else:
        print(output_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
