#!/usr/bin/env python3
"""Check disponibilita MCP server per /lead-finder-pro (best-effort, no live ping).

Legge ~/.claude.json (user scope) + .claude/mcp_settings.json (project scope).
Restituisce JSON {server_name: {available: bool, scope: 'user'|'project'|'none'}}.

Usage: python scripts/mcp_detect.py [--check SERVER]
Author: Filippo Greco / lead-finder-pro 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

DEFAULT_SERVERS = [
    "hunter",
    "attio-mcp",
    "explorium",
    "smartlead",
    "heyreach",
    "google-personal",
    "playwright",
]


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON in {path}: {e}")
        return None


def collect_servers_from_user_config() -> dict:
    """Read ~/.claude.json user scope and extract mcpServers entries."""
    user_config = Path.home() / ".claude.json"
    data = load_json(user_config) or {}
    return data.get("mcpServers", {}) or {}


def collect_servers_from_project_config(project_root: Path) -> dict:
    """Read .claude/mcp_settings.json or .mcp.json project scope."""
    candidates = [
        project_root / ".claude" / "mcp_settings.json",
        project_root / ".mcp.json",
    ]
    for path in candidates:
        data = load_json(path)
        if data:
            return data.get("mcpServers", {}) or {}
    return {}


def detect_servers(servers: list[str], project_root: Path) -> dict:
    user_servers = collect_servers_from_user_config()
    project_servers = collect_servers_from_project_config(project_root)
    result = {}
    for name in servers:
        if name in project_servers:
            result[name] = {"available": True, "scope": "project"}
        elif name in user_servers:
            result[name] = {"available": True, "scope": "user"}
        else:
            result[name] = {"available": False, "scope": "none"}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect MCP servers for /lead-finder-pro"
    )
    parser.add_argument("--check", help="Check single server (default: all)")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: cwd)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    servers = [args.check] if args.check else DEFAULT_SERVERS
    result = detect_servers(servers, project_root)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
