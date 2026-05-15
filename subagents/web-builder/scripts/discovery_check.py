#!/usr/bin/env python3
"""discovery_check.py — verifica/load config /web-builder.

Usage:
    python3 discovery_check.py --project-path <path>           # check if config exists
    python3 discovery_check.py --project-path <path> --validate  # validate schema
    python3 discovery_check.py --project-path <path> --print     # print config to stdout

Output JSON:
    {
        "config_exists": bool,
        "config_path": str,
        "schema_valid": bool,
        "errors": [str],
        "config": dict | null
    }
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        json.dumps(
            {
                "config_exists": False,
                "errors": ["PyYAML not installed. Run: pip install pyyaml"],
            }
        )
    )
    sys.exit(1)


REQUIRED_FIELDS = {
    "project": ["name", "path", "type"],
    "user": ["experience", "language_preference"],
    "stack": ["framework", "database", "auth", "deploy"],
    "build": ["last_step_completed"],
}

VALID_VALUES = {
    "project.type": [
        "landing",
        "saas_micro",
        "internal_tool",
        "content",
        "mobile",
    ],
    "user.experience": ["zero", "vibe_coder", "junior", "senior"],
    "stack.framework": [
        "nextjs_15",
        "astro",
        "sveltekit",
        "expo",
        "no-code",
    ],
    "stack.database": ["convex", "supabase", "none", "sanity"],
    "stack.auth": ["clerk", "workos", "supabase_auth", "none", "custom"],
    "stack.deploy": ["vercel", "netlify", "cloudflare", "railway"],
}


def find_config(project_path: Path) -> Path | None:
    """Find config.md in standard locations."""
    candidates = [
        project_path / ".claude" / "web-builder" / "config.md",
        project_path / ".claude" / "memory" / "config.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_config(config_path: Path) -> tuple[dict | None, list[str]]:
    """Parse YAML frontmatter from config.md."""
    errors: list[str] = []
    try:
        content = config_path.read_text()
    except OSError as e:
        return None, [f"Cannot read {config_path}: {e}"]

    if not content.startswith("---"):
        return None, ["config.md must start with YAML frontmatter (---)"]

    try:
        end_idx = content.index("---", 3)
        frontmatter = content[3:end_idx].strip()
    except ValueError:
        return None, ["YAML frontmatter not closed (missing second ---)"]

    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        return None, [f"YAML parse error: {e}"]

    return data, errors


def validate_schema(config: dict) -> list[str]:
    """Validate config against schema."""
    errors: list[str] = []

    for section, fields in REQUIRED_FIELDS.items():
        if section not in config:
            errors.append(f"Missing section: {section}")
            continue
        for field in fields:
            if field not in config[section]:
                errors.append(f"Missing field: {section}.{field}")

    for path, valid in VALID_VALUES.items():
        section, field = path.split(".")
        if section in config and field in config[section]:
            value = config[section][field]
            if value not in valid:
                errors.append(f"Invalid value for {path}: '{value}'. Valid: {valid}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-path", required=True, help="Path to project root")
    parser.add_argument("--validate", action="store_true", help="Validate schema")
    parser.add_argument("--print", action="store_true", help="Print config")
    args = parser.parse_args()

    project_path = Path(args.project_path).expanduser().resolve()
    if not project_path.exists():
        print(
            json.dumps(
                {
                    "config_exists": False,
                    "errors": [f"Project path not exist: {project_path}"],
                }
            )
        )
        return 1

    config_path = find_config(project_path)
    result: dict = {
        "config_exists": config_path is not None,
        "config_path": str(config_path) if config_path else None,
        "schema_valid": False,
        "errors": [],
        "config": None,
    }

    if config_path is None:
        print(json.dumps(result, indent=2))
        return 0

    config, parse_errors = parse_config(config_path)
    if parse_errors:
        result["errors"] = parse_errors
        print(json.dumps(result, indent=2))
        return 1

    result["config"] = config

    if args.validate or args.print:
        validation_errors = validate_schema(config or {})
        result["schema_valid"] = len(validation_errors) == 0
        result["errors"] = validation_errors

    print(json.dumps(result, indent=2, default=str))
    return 0 if result["schema_valid"] or not args.validate else 1


if __name__ == "__main__":
    sys.exit(main())
