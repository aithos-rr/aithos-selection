#!/usr/bin/env python3
"""
mcp_detect.py — Detect MCP server availability for /outbound-orchestrator

Usage:
    python mcp_detect.py [--output-json <path>]

Output: JSON with {server: {available: bool, scope: 'user'|'project'|'none'}}
for: smartlead, heyreach, attio-mcp, google-personal, claude_ai_Gmail.

NOTE: This script CANNOT directly invoke MCP tools (those are subagent-only).
It checks if env vars + config files indicate availability.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# MCP servers to check
MCP_SERVERS = [
    "smartlead",
    "heyreach",
    "attio-mcp",
    "google-personal",
    "claude_ai_Gmail",
]


def check_env_var(var_names):
    """Check if any env var name is set."""
    for v in var_names:
        if os.environ.get(v):
            return True
    return False


def check_config_files(server):
    """Check ~/.claude.json or settings.local.json mentions this server."""
    paths = [
        Path.home() / ".claude.json",
        Path.cwd() / ".claude" / "settings.local.json",
        Path.cwd() / ".claude" / "settings.json",
    ]
    for path in paths:
        if not path.exists():
            continue
        try:
            with open(path) as f:
                content = f.read()
                if server in content or server.replace("-", "_") in content:
                    return True
        except Exception:
            continue
    return False


def detect_mcp_status():
    """Build status dict per server."""
    status = {}

    # smartlead — check env + config
    smartlead_env = check_env_var(["SMARTLEAD_API_KEY"])
    smartlead_config = check_config_files("smartlead")
    status["smartlead"] = {
        "available": smartlead_env or smartlead_config,
        "scope": "user"
        if smartlead_config
        else ("env_only" if smartlead_env else "none"),
        "api_key_present": smartlead_env,
    }

    # heyreach — check env + config
    heyreach_env = check_env_var(["HEYREACH_API_KEY"])
    heyreach_config = check_config_files("heyreach")
    status["heyreach"] = {
        "available": heyreach_env or heyreach_config,
        "scope": "user"
        if heyreach_config
        else ("env_only" if heyreach_env else "none"),
        "api_key_present": heyreach_env,
    }

    # attio-mcp — check config (no specific env var)
    attio_config = check_config_files("attio")
    status["attio-mcp"] = {
        "available": attio_config,
        "scope": "user" if attio_config else "none",
    }

    # google-personal — check config
    google_config = check_config_files("google-personal") or check_config_files(
        "google_personal"
    )
    status["google-personal"] = {
        "available": google_config,
        "scope": "user" if google_config else "none",
    }

    # claude_ai_Gmail (Claude.ai integration)
    gmail_config = check_config_files("claude_ai_Gmail") or check_config_files("Gmail")
    status["claude_ai_Gmail"] = {
        "available": gmail_config,
        "scope": "user" if gmail_config else "none",
    }

    return status


def get_fallbacks(status):
    """Map missing MCP to fallback strategy."""
    fallbacks = {}
    if not status["smartlead"]["available"]:
        fallbacks["smartlead"] = "csv_export_for_manual_import"
    if not status["heyreach"]["available"]:
        fallbacks["heyreach"] = "csv_export_with_linkedin_urls"
    if not status["attio-mcp"]["available"]:
        fallbacks["attio-mcp"] = "skip_crm_sync_log_only"
    if not status["google-personal"]["available"]:
        fallbacks["google-personal"] = "markdown_local_output"
    if not status["claude_ai_Gmail"]["available"]:
        fallbacks["claude_ai_Gmail"] = "log_only_manual_forward"
    return fallbacks


def main():
    parser = argparse.ArgumentParser(
        description="MCP detection for /outbound-orchestrator"
    )
    parser.add_argument("--output-json", help="Save detection result to JSON file")
    args = parser.parse_args()

    status = detect_mcp_status()
    fallbacks = get_fallbacks(status)

    result = {
        "checked_at": datetime.now().isoformat(),
        "agent": "outbound-orchestrator",
        "mcp_status": status,
        "mcp_fallbacks_active": fallbacks,
        "summary": {
            "available": [s for s, info in status.items() if info["available"]],
            "missing": [s for s, info in status.items() if not info["available"]],
        },
    }

    # Print summary
    print("📡 MCP detection result:")
    print(f"\nAvailable ({len(result['summary']['available'])}):")
    for s in result["summary"]["available"]:
        print(f"  ✓ {s}")

    print(f"\nMissing ({len(result['summary']['missing'])}):")
    for s in result["summary"]["missing"]:
        fb = fallbacks.get(s, "no_fallback")
        print(f"  ✗ {s} → fallback: {fb}")

    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved: {args.output_json}")
    else:
        print(f"\n{json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
