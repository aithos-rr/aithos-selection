#!/usr/bin/env python3
"""mcp_detect.py — Detect available MCP servers for /automation-architect.

Probes critical MCPs (n8n-knowledge, n8n-yellowtech, n8n-filippo, context7, parallel-cli)
and outputs availability map. Used at first-run by /automation-architect to populate
config.mcp_available.

Usage: python3 mcp_detect.py [--config <memory_dir>/config.md]
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


CRITICAL_MCPS = [
    {"name": "n8n-knowledge", "tier": "primary", "fallback": "WebFetch n8n docs"},
    {
        "name": "n8n-yellowtech",
        "tier": "recommended",
        "fallback": "JSON file output, manual import",
    },
    {
        "name": "n8n-filippo",
        "tier": "recommended",
        "fallback": "JSON file output, manual import",
    },
    {"name": "context7", "tier": "optional", "fallback": "WebFetch direct"},
]


def check_parallel_cli() -> bool:
    """Probe if parallel-cli is in PATH."""
    return shutil.which("parallel-cli") is not None


def detect_mcps_from_config() -> dict:
    """Read ~/.claude.json or .claude/.mcp.json to enumerate configured MCPs."""
    config_paths = [
        Path.home() / ".claude.json",
        Path.cwd() / ".claude" / ".mcp.json",
        Path.cwd() / ".mcp.json",
    ]
    detected = {}
    for path in config_paths:
        if not path.exists():
            continue
        try:
            cfg = json.loads(path.read_text())
            mcps = cfg.get("mcpServers", {}) or cfg.get("mcp", {}).get("servers", {})
            for name in mcps:
                detected[name] = {"configured": True, "source": str(path)}
        except (json.JSONDecodeError, KeyError):
            continue
    return detected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to write config snippet")
    args = parser.parse_args()

    detected_mcps = detect_mcps_from_config()
    parallel_cli_ok = check_parallel_cli()

    result = {
        "mcp_available": {},
        "fallbacks_active": {},
        "tools_status": {"parallel-cli": parallel_cli_ok},
    }

    for mcp in CRITICAL_MCPS:
        name = mcp["name"]
        if name in detected_mcps:
            result["mcp_available"][name] = True
        else:
            result["mcp_available"][name] = False
            result["fallbacks_active"][name] = mcp["fallback"]

    result["mcp_available"]["parallel-cli"] = parallel_cli_ok
    if not parallel_cli_ok:
        result["fallbacks_active"]["parallel-cli"] = "WebSearch"

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.config:
        snippet = "\n# MCP availability (auto-detected)\n"
        snippet += f"mcp_available: {json.dumps(result['mcp_available'])}\n"
        snippet += f"mcp_fallbacks_active: {json.dumps(result['fallbacks_active'])}\n"
        Path(args.config).write_text(snippet, encoding="utf-8")
        print(f"\n✓ Config snippet written to {args.config}", file=sys.stderr)


if __name__ == "__main__":
    main()
