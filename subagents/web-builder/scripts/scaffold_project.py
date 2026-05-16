#!/usr/bin/env python3
"""scaffold_project.py — copy template + placeholder substitution + git init.

Usage:
    python3 scaffold_project.py \
        --template-id nextjs-saas \
        --project-name my-saas \
        --project-path /path/to/my-saas \
        [--author "Filippo Greco"] \
        [--domain "my-saas.com"] \
        [--description "SaaS for X"] \
        [--dry-run] \
        [--force]

Output JSON:
    {
        "status": "success" | "partial" | "failed",
        "path": "...",
        "files_created": [...],
        "git_initialized": bool,
        "warnings": [...],
        "next_steps": [...]
    }
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

VALID_TEMPLATES = [
    "nextjs-saas",
    "nextjs-landing",
    "astro-marketing",
    "next-internal-tool",
    "expo-mobile",
]

# File extension to substitute placeholders in
SUBST_EXTENSIONS = {
    ".json",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".md",
    ".astro",
    ".mjs",
    ".cjs",
    ".html",
    ".css",
    ".env",
    ".example",
    ".gitignore",
    ".yml",
    ".yaml",
    ".toml",
}


def to_title_case(s: str) -> str:
    """Convert kebab-case to Title Case."""
    return " ".join(word.capitalize() for word in s.split("-"))


def is_valid_kebab_case(name: str) -> bool:
    """Check if string is valid kebab-case (lowercase + hyphens)."""
    return bool(re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name))


def substitute_placeholders(content: str, replacements: dict[str, str]) -> str:
    """Replace {{KEY}} or {{ KEY }} (formatter-added spaces) with values."""
    for key, val in replacements.items():
        # Match {{KEY}} or {{ KEY }} (any whitespace inside)
        pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
        content = re.sub(pattern, lambda m, v=val: v, content)
    return content


def copy_template(
    template_dir: Path,
    project_path: Path,
    replacements: dict[str, str],
    dry_run: bool = False,
) -> tuple[list[str], list[str]]:
    """Copy template files + substitute placeholders. Returns (files_created, warnings)."""
    files_created: list[str] = []
    warnings: list[str] = []

    for src in template_dir.rglob("*"):
        if src.is_dir():
            continue

        # Skip node_modules, .next, build artifacts (defensive)
        rel_parts = src.relative_to(template_dir).parts
        if any(p in {"node_modules", ".next", "dist", ".git"} for p in rel_parts):
            warnings.append(
                f"Skipped (build artifact): {src.relative_to(template_dir)}"
            )
            continue

        rel_path = src.relative_to(template_dir)
        dest = project_path / rel_path

        if dry_run:
            files_created.append(str(rel_path))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        # Substitute only on text files with known extensions
        suffix = src.suffix.lower()
        is_text = suffix in SUBST_EXTENSIONS or src.name in {
            ".gitignore",
            ".env.example",
            ".env.local.example",
            "Dockerfile",
        }

        if is_text:
            try:
                content = src.read_text(encoding="utf-8")
                new_content = substitute_placeholders(content, replacements)
                dest.write_text(new_content, encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(src, dest)
                warnings.append(f"Binary file in text dir, copied as-is: {rel_path}")
        else:
            shutil.copy2(src, dest)

        files_created.append(str(rel_path))

    return files_created, warnings


def init_git(project_path: Path, stack_summary: str) -> bool:
    """Init git repo + initial commit. Returns True if success."""
    try:
        subprocess.run(
            ["git", "init", "--initial-branch=main"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", ".gitignore", "package.json", "README.md"],
            cwd=project_path,
            check=False,
            capture_output=True,
        )
        # Add code dirs if exist (selective, NO git add -A)
        for dirname in ("app", "src", "public", "convex", "lib", "components"):
            if (project_path / dirname).exists():
                subprocess.run(
                    ["git", "add", dirname],
                    cwd=project_path,
                    check=False,
                    capture_output=True,
                )
        # Add config files
        for fname in (
            "tsconfig.json",
            "next.config.ts",
            "next.config.mjs",
            "next.config.js",
            "astro.config.mjs",
            "tailwind.config.ts",
            "components.json",
            ".env.local.example",
            "CLAUDE.md",
        ):
            if (project_path / fname).exists():
                subprocess.run(
                    ["git", "add", fname],
                    cwd=project_path,
                    check=False,
                    capture_output=True,
                )

        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Initial scaffold via /web-builder — {stack_summary}",
            ],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-id", required=True, choices=VALID_TEMPLATES)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-path", required=True)
    parser.add_argument("--author", default="You")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--description", default=None)
    parser.add_argument("--stack-summary", default="custom stack")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow scaffold in non-empty dir (no merge logic)",
    )
    parser.add_argument("--no-git", action="store_true", help="Skip git init")
    args = parser.parse_args()

    project_name = args.project_name
    if not is_valid_kebab_case(project_name):
        print(
            json.dumps(
                {
                    "status": "failed",
                    "errors": [
                        f"Invalid project name '{project_name}'. Use kebab-case (lowercase, hyphens)."
                    ],
                }
            )
        )
        return 1

    project_path = Path(args.project_path).expanduser().resolve()
    template_dir = TEMPLATES_DIR / args.template_id

    if not template_dir.exists():
        print(
            json.dumps(
                {
                    "status": "failed",
                    "errors": [
                        f"Template '{args.template_id}' not found at {template_dir}"
                    ],
                }
            )
        )
        return 1

    # Check destination
    if project_path.exists() and any(project_path.iterdir()) and not args.force:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "errors": [
                        f"Path exists and not empty: {project_path}. Use --force or merge mode."
                    ],
                }
            )
        )
        return 1

    project_path.mkdir(parents=True, exist_ok=True)

    replacements = {
        "PROJECT_NAME": project_name,
        "PROJECT_NAME_TITLE": to_title_case(project_name),
        "AUTHOR": args.author,
        "DOMAIN": args.domain or f"{project_name}.vercel.app",
        "DESCRIPTION": args.description
        or f"{to_title_case(project_name)} built with /web-builder",
        "YEAR": str(datetime.now().year),
    }

    files_created, warnings = copy_template(
        template_dir, project_path, replacements, dry_run=args.dry_run
    )

    git_initialized = False
    if not args.dry_run and not args.no_git:
        git_initialized = init_git(project_path, args.stack_summary)

    next_steps = [
        "Phase 3: compile CLAUDE.md (skill claude-md-generator)",
        "Phase 4: setup auth + DB (skill auth-database-setup)",
        f"Test locale: cd {project_path} && npm install && npm run dev",
    ]

    output = {
        "status": "success" if files_created else "partial",
        "path": str(project_path),
        "template_id": args.template_id,
        "files_created": files_created,
        "files_count": len(files_created),
        "git_initialized": git_initialized,
        "dry_run": args.dry_run,
        "warnings": warnings,
        "next_steps": next_steps,
    }

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
