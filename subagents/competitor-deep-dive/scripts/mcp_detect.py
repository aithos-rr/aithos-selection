#!/usr/bin/env python3
"""Verifica disponibilità MCP server + CLI per /competitor-deep-dive.

Usage: python scripts/mcp_detect.py [--claude-config PATH] [--check-cli]
Author: Filippo Greco / competitor-deep-dive 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

# MCP server names + scope
MCP_SERVERS_REQUIRED = ["apify", "playwright"]
MCP_SERVERS_RECOMMENDED = ["google-personal", "slack", "attio-mcp"]
CLI_TOOLS = ["parallel-cli", "notebooklm"]


def load_claude_config(config_path: Path) -> dict:
    """Load ~/.claude.json or .mcp.json."""
    if not config_path.exists():
        log.warning(f"Config not found: {config_path}")
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log.error(f"JSON parse error: {e}")
        return {}


def detect_mcp_in_config(config: dict, server_name: str) -> dict:
    """Search server in user-scope or project-scope mcpServers."""
    # User scope: top-level mcpServers
    user_servers = config.get("mcpServers", {})
    if server_name in user_servers:
        return {"available": True, "scope": "user", "config": user_servers[server_name]}

    # Project scope: projects[<cwd>].mcpServers
    cwd = str(Path.cwd())
    projects = config.get("projects", {})
    for proj_path, proj_config in projects.items():
        if cwd.startswith(proj_path) or proj_path in cwd:
            proj_servers = proj_config.get("mcpServers", {})
            if server_name in proj_servers:
                return {
                    "available": True,
                    "scope": "project",
                    "config": proj_servers[server_name],
                }

    return {"available": False, "scope": "none"}


def detect_cli_tool(name: str) -> dict:
    """Check CLI tool in PATH."""
    binary = shutil.which(name)
    if binary:
        try:
            result = subprocess.run(
                [name, "--version"], capture_output=True, text=True, timeout=5
            )
            version = result.stdout.strip() or result.stderr.strip()
            return {"available": True, "path": binary, "version": version[:100]}
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return {"available": True, "path": binary, "version": "unknown"}
    return {"available": False, "path": None}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect MCP servers + CLI tools per /competitor-deep-dive"
    )
    parser.add_argument(
        "--claude-config",
        default=str(Path.home() / ".claude.json"),
        help="Path to ~/.claude.json (default: $HOME/.claude.json)",
    )
    parser.add_argument(
        "--check-cli",
        action="store_true",
        default=True,
        help="Also check CLI tools (parallel-cli, notebooklm)",
    )
    args = parser.parse_args()

    config_path = (
        Path(args.claude - config) if False else Path(args.claude_config).expanduser()
    )
    config = load_claude_config(config_path)

    result = {
        "mcp_required": {},
        "mcp_recommended": {},
        "cli_tools": {},
        "summary": {},
    }

    # Required MCPs
    for server in MCP_SERVERS_REQUIRED:
        info = detect_mcp_in_config(config, server)
        result["mcp_required"][server] = info

    # Recommended MCPs
    for server in MCP_SERVERS_RECOMMENDED:
        info = detect_mcp_in_config(config, server)
        result["mcp_recommended"][server] = info

    # CLI tools
    if args.check_cli:
        for tool in CLI_TOOLS:
            result["cli_tools"][tool] = detect_cli_tool(tool)

    # Summary
    required_available = sum(
        1 for s in MCP_SERVERS_REQUIRED if result["mcp_required"][s]["available"]
    )
    recommended_available = sum(
        1 for s in MCP_SERVERS_RECOMMENDED if result["mcp_recommended"][s]["available"]
    )
    cli_available = sum(
        1 for t in CLI_TOOLS if result["cli_tools"].get(t, {}).get("available")
    )

    result["summary"] = {
        "required_available": f"{required_available}/{len(MCP_SERVERS_REQUIRED)}",
        "recommended_available": f"{recommended_available}/{len(MCP_SERVERS_RECOMMENDED)}",
        "cli_available": f"{cli_available}/{len(CLI_TOOLS)}",
        "ready_to_run": required_available == len(MCP_SERVERS_REQUIRED),
        "fallbacks_active": [],
    }

    # Compute fallbacks_active
    if not result["mcp_required"]["apify"]["available"]:
        result["summary"]["fallbacks_active"].append(
            "apify->parallel-cli+WebFetch (HIGH degraded — no structured reviews)"
        )
    if not result["mcp_required"]["playwright"]["available"]:
        result["summary"]["fallbacks_active"].append(
            "playwright->curl+html parse (MEDIUM degraded — no JS render)"
        )
    if not result["mcp_recommended"]["google-personal"]["available"]:
        result["summary"]["fallbacks_active"].append(
            "google-personal->markdown locale (NONE if not requested)"
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
