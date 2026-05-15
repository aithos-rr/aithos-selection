#!/usr/bin/env python3
"""mcp_detect.py — detect MCP servers configured for /web-builder.

Reads ~/.claude.json e .claude/settings.local.json + .claude/mcp.json per identify
configured MCP servers. Returns availability per server name.

Usage:
    python3 mcp_detect.py [--project-path <path>] [--server <name>]

Output JSON:
    {
        "vercel": {"configured": true, "transport": "http", "url": "https://mcp.vercel.com"},
        "github": {"configured": false},
        "context7": {"configured": true, "command": "..."},
        ...
    }
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


TARGET_SERVERS = [
    "vercel",
    "github",
    "context7",
    "playwright",
    "apify",
    "n8n-default",
    "n8n-knowledge",
    "n8n-filippo",
    "n8n-workspace_b-tools",
]


def read_json_safe(path: Path) -> dict:
    """Read JSON file safely, return empty dict if not exist or invalid."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def find_mcp_configs(project_path: Path) -> list[Path]:
    """List MCP config files searched, in priority order (most local first)."""
    home = Path.home()
    return [
        project_path / ".mcp.json",
        project_path / ".claude" / "mcp.json",
        project_path / ".claude" / "settings.local.json",
        home / ".claude.json",
        home / ".claude" / "settings.json",
    ]


def extract_mcp_servers(config: dict) -> dict[str, dict]:
    """Extract mcpServers section from config dict (different schemas)."""
    if "mcpServers" in config:
        return config["mcpServers"]
    if "projects" in config:
        for proj in config["projects"].values():
            if "mcpServers" in proj:
                return proj["mcpServers"]
    return {}


def detect_servers(project_path: Path) -> dict:
    """Detect MCP servers from all config files."""
    detected: dict[str, dict] = {}

    for cfg_path in find_mcp_configs(project_path):
        cfg = read_json_safe(cfg_path)
        if not cfg:
            continue
        servers = extract_mcp_servers(cfg)
        for name, info in servers.items():
            if name not in detected:
                detected[name] = {
                    "configured": True,
                    "source": str(cfg_path),
                    **{
                        k: v
                        for k, v in info.items()
                        if k in ("command", "url", "transport", "type")
                    },
                }

    return detected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-path",
        default=os.getcwd(),
        help="Project path (default: cwd)",
    )
    parser.add_argument(
        "--server",
        help="Check single server. Returns 0 if configured, 1 otherwise.",
    )
    args = parser.parse_args()

    project_path = Path(args.project_path).expanduser().resolve()
    detected = detect_servers(project_path)

    if args.server:
        info = detected.get(args.server, {"configured": False})
        print(json.dumps({args.server: info}, indent=2))
        return 0 if info.get("configured") else 1

    result: dict = {}
    for server in TARGET_SERVERS:
        result[server] = detected.get(server, {"configured": False})

    other = {n: i for n, i in detected.items() if n not in TARGET_SERVERS}
    if other:
        result["_other_configured"] = list(other.keys())

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
