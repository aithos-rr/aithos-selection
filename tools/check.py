"""Repository validator for aithos-selection.

Runs all repository invariants in a single pass and exits non-zero on
failure. Discovery is delegated to :mod:`generate_index` so the catalog
logic stays in one place.

CLI:
    uv run python tools/check.py             # validate, exit 1 on failure
    uv run python tools/check.py --fix       # regenerate INDEX.md if stale,
                                             # then re-validate
"""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Annotated, Literal, Optional, Union

import typer
import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from rich.console import Console
from rich.table import Table

# Make ``import generate_index`` work whether check.py is invoked directly
# (``python tools/check.py``) or via uv (``uv run python tools/check.py``).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_index as gi  # noqa: E402

ROOT: Path = gi.ROOT
console = Console()


# ---------------------------------------------------------------------------
# Strict schema models — mirror docs/schemas/{frontmatter,manifest}.schema.yaml
# These add the regex patterns and enums that the lenient models in
# generate_index.py deliberately omit (those exist to keep discovery
# resilient when an atom is mid-edit).
# ---------------------------------------------------------------------------


KEBAB_RE = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SEMVER_RE = r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"
DATE_RE = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"


KebabStr = Annotated[str, Field(pattern=KEBAB_RE)]


def _validate_iso_date(v: Union[date, str]) -> Union[date, str]:
    """Accept PyYAML-parsed ``datetime.date`` or a ``YYYY-MM-DD`` string."""
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        if not re.match(DATE_RE, v):
            raise ValueError("date must match YYYY-MM-DD")
        return v
    raise ValueError("date must be a YYYY-MM-DD string or a date literal")


class StrictAtomFrontmatter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: KebabStr
    name: str = Field(min_length=1)
    type: Literal["prompt", "template", "stack-note", "skill"]
    status: Literal["draft", "stable", "deprecated"]
    version: str = Field(pattern=SEMVER_RE)
    description: str = Field(min_length=1)
    tags: list[KebabStr] = []
    language: Literal["it", "en", "multilingual"]
    model: Optional[str] = None
    created: Union[date, str]
    updated: Union[date, str]
    author: str = Field(min_length=1)

    _validate_created = field_validator("created")(_validate_iso_date)
    _validate_updated = field_validator("updated")(_validate_iso_date)


URL_RE = r"^https?://"


class StrictReferenceFrontmatter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: KebabStr
    name: str = Field(min_length=1)
    type: Literal["reference"]
    subtype: Literal["repo", "article", "template"]
    url: str = Field(pattern=URL_RE)
    status: Literal["active", "archived", "broken"]
    description: str = Field(min_length=1)
    tags: list[KebabStr] = []
    language: Literal["it", "en", "multilingual"]
    created: Union[date, str]
    updated: Union[date, str]
    author: str = Field(min_length=1)

    # Optional GitHub-specific fields (only meaningful when subtype: repo)
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    github_stars: Optional[int] = Field(default=None, ge=0)
    github_language: Optional[str] = None
    github_topics: list[str] = []
    github_last_commit: Optional[Union[date, str]] = None

    _validate_created = field_validator("created")(_validate_iso_date)
    _validate_updated = field_validator("updated")(_validate_iso_date)
    _validate_last_commit = field_validator("github_last_commit")(
        lambda v: v if v is None else _validate_iso_date(v)
    )


class StrictManifestUses(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompts: list[str] = []
    templates: list[str] = []
    mcp_servers: list[str] = []
    tools: list[str] = []


class StrictManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: KebabStr
    version: str = Field(pattern=SEMVER_RE)
    type: Literal["agent", "workflow"]
    description: str = Field(min_length=1)
    status: Literal["draft", "stable", "deprecated"]
    tags: list[KebabStr] = []
    created: Union[date, str]
    updated: Union[date, str]
    system_prompt: Optional[str] = None
    uses: Optional[StrictManifestUses] = None
    agents: list[str] = []
    n8n_workflows: list[str] = []

    _validate_created = field_validator("created")(_validate_iso_date)
    _validate_updated = field_validator("updated")(_validate_iso_date)

    @model_validator(mode="after")
    def _enforce_type_rules(self) -> "StrictManifest":
        if self.type == "agent" and not self.system_prompt:
            raise ValueError(
                "system_prompt is required when type is 'agent'"
            )
        if self.type == "workflow" and len(self.agents) < 1:
            raise ValueError(
                "workflows must declare at least one entry in 'agents'"
            )
        return self


# ---------------------------------------------------------------------------
# Check result type
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    passed: bool
    summary: str = ""
    details: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rel(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


def _format_validation_error(exc: ValidationError) -> list[str]:
    return [
        f"  · {'.'.join(str(x) for x in e['loc']) or '<root>'}: {e['msg']}"
        for e in exc.errors()
    ]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_manifest_schema(root: Path) -> CheckResult:
    manifests = sorted(
        list((root / "agents").glob("*/manifest.yaml"))
        + list((root / "workflows").glob("*/manifest.yaml"))
    )
    details: list[str] = []
    valid = 0
    for m in manifests:
        try:
            raw = yaml.safe_load(m.read_text(encoding="utf-8")) or {}
            StrictManifest(**raw)
            valid += 1
        except ValidationError as exc:
            details.append(f"{_rel(m)}: {exc.error_count()} schema error(s)")
            details.extend(_format_validation_error(exc))
        except Exception as exc:
            details.append(f"{_rel(m)}: {type(exc).__name__}: {exc}")
    passed = not details
    summary = f"{valid}/{len(manifests)} manifest(s) valid"
    return CheckResult("Manifest schema compliance", passed, summary, details)


def check_frontmatter_schema(root: Path) -> CheckResult:
    targets: list[tuple[Path, str]] = []
    for p in sorted((root / "prompts" / "library").glob("*.md")):
        if p.name == "README.md":
            continue
        targets.append((p, "atom"))
    for p in sorted((root / "prompts" / "templates").glob("*.md")):
        if p.name == "README.md":
            continue
        targets.append((p, "atom"))
    for p in sorted((root / "stack").glob("*.md")):
        if p.name == "README.md":
            continue
        targets.append((p, "atom"))
    for p in sorted((root / "skills").glob("*/SKILL.md")):
        targets.append((p, "skill"))

    details: list[str] = []
    valid = 0
    for p, kind in targets:
        try:
            fm = gi._read_frontmatter(p)
            if fm is None:
                details.append(f"{_rel(p)}: no frontmatter block")
                continue
            if kind == "skill":
                gi.SkillFrontmatter(**fm)
            else:
                StrictAtomFrontmatter(**fm)
            valid += 1
        except ValidationError as exc:
            details.append(f"{_rel(p)}: {exc.error_count()} schema error(s)")
            details.extend(_format_validation_error(exc))
        except Exception as exc:
            details.append(f"{_rel(p)}: {type(exc).__name__}: {exc}")
    passed = not details
    summary = f"{valid}/{len(targets)} file(s) valid"
    return CheckResult(
        "Frontmatter schema compliance", passed, summary, details
    )


_REFERENCE_FOLDER_TO_SUBTYPE = {
    "repos": "repo",
    "articles": "article",
    "templates": "template",
}


def _reference_markdown_files(root: Path) -> list[tuple[Path, str]]:
    """Return ``(path, expected_subtype)`` pairs for every reference file."""
    out: list[tuple[Path, str]] = []
    refs_root = root / "references"
    if not refs_root.is_dir():
        return out
    for folder, expected in _REFERENCE_FOLDER_TO_SUBTYPE.items():
        sub = refs_root / folder
        if not sub.is_dir():
            continue
        for p in sorted(sub.glob("*.md")):
            if p.name == "README.md":
                continue
            out.append((p, expected))
    return out


def check_reference_schema_compliance(root: Path) -> CheckResult:
    targets = _reference_markdown_files(root)
    details: list[str] = []
    valid = 0
    for p, _expected_subtype in targets:
        try:
            fm = gi._read_frontmatter(p)
            if fm is None:
                details.append(f"{_rel(p)}: no frontmatter block")
                continue
            StrictReferenceFrontmatter(**fm)
            valid += 1
        except ValidationError as exc:
            details.append(f"{_rel(p)}: {exc.error_count()} schema error(s)")
            details.extend(_format_validation_error(exc))
        except Exception as exc:
            details.append(f"{_rel(p)}: {type(exc).__name__}: {exc}")
    passed = not details
    summary = f"{valid}/{len(targets)} reference(s) valid"
    return CheckResult(
        "Reference schema compliance", passed, summary, details
    )


def check_reference_subtype_folder_match(root: Path) -> CheckResult:
    targets = _reference_markdown_files(root)
    details: list[str] = []
    checked = 0
    for p, expected_subtype in targets:
        try:
            fm = gi._read_frontmatter(p)
        except Exception as exc:
            details.append(f"{_rel(p)}: {type(exc).__name__}: {exc}")
            continue
        if fm is None:
            # Already flagged by the schema check; skip silently here.
            continue
        checked += 1
        actual = fm.get("subtype")
        if actual != expected_subtype:
            details.append(
                f"{_rel(p)}: subtype {actual!r} does not match parent "
                f"folder (expected {expected_subtype!r})"
            )
    passed = not details
    summary = f"{checked} reference(s) checked"
    return CheckResult(
        "Reference subtype/folder match", passed, summary, details
    )


def check_broken_references(root: Path) -> CheckResult:
    """Every path referenced by a manifest must resolve to a real file or
    directory."""
    composites, _ = gi.discover_composites_with_failures(root)
    recipes, _ = gi.discover_recipes_with_failures(root)
    details: list[str] = []
    checked = 0

    def _check_root_relative(
        owner: str, kind: str, path_str: str, must_be_dir: bool = False
    ) -> None:
        nonlocal checked
        checked += 1
        target = (root / path_str).resolve()
        if must_be_dir:
            if not target.is_dir():
                details.append(
                    f"{owner}: {kind} → '{path_str}' is not an existing "
                    f"directory"
                )
        else:
            if not target.exists():
                details.append(
                    f"{owner}: {kind} → '{path_str}' does not exist"
                )

    for c in composites:
        manifest_path = root / c.path / "manifest.yaml"
        owner = _rel(manifest_path)
        # system_prompt is relative to the manifest
        if c.system_prompt:
            checked += 1
            target = (manifest_path.parent / c.system_prompt).resolve()
            if not target.is_file():
                details.append(
                    f"{owner}: system_prompt → '{c.system_prompt}' "
                    f"does not resolve to a file"
                )
        for kind, paths in (
            ("uses.prompts", c.uses_prompts),
            ("uses.templates", c.uses_templates),
            ("uses.mcp_servers", c.uses_mcp),
            ("uses.tools", c.uses_tools),
        ):
            for p in paths:
                _check_root_relative(owner, kind, p)

    for r in recipes:
        manifest_path = root / r.path / "manifest.yaml"
        owner = _rel(manifest_path)
        for ap in r.agents:
            _check_root_relative(owner, "agents", ap, must_be_dir=True)
        for kind, paths in (
            ("uses.prompts", r.uses_prompts),
            ("uses.templates", r.uses_templates),
            ("uses.mcp_servers", r.uses_mcp),
            ("uses.tools", r.uses_tools),
            ("n8n_workflows", r.n8n_workflows),
        ):
            for p in paths:
                _check_root_relative(owner, kind, p)

    passed = not details
    summary = f"{checked} reference(s) checked"
    return CheckResult("No broken references", passed, summary, details)


def check_no_duplicate_atoms(root: Path) -> CheckResult:
    """Hash the body of each frontmatter-bearing atom; flag duplicates.
    Warn (do not fail) on duplicate ``id`` or ``name`` fields."""
    bodies: dict[str, list[str]] = {}
    ids: dict[str, list[str]] = {}

    md_globs = [
        root / "prompts" / "library",
        root / "prompts" / "templates",
        root / "stack",
    ]
    for d in md_globs:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name == "README.md":
                continue
            text = p.read_text(encoding="utf-8")
            m = gi.FRONTMATTER_RE.match(text)
            if not m:
                continue
            body = text[m.end():]
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            bodies.setdefault(digest, []).append(_rel(p))
            fm = yaml.safe_load(m.group(1)) or {}
            atom_id = fm.get("id")
            if isinstance(atom_id, str):
                ids.setdefault(atom_id, []).append(_rel(p))

    # Manifest name collisions (warnings only)
    manifest_names: dict[str, list[str]] = {}
    for m in sorted(
        list((root / "agents").glob("*/manifest.yaml"))
        + list((root / "workflows").glob("*/manifest.yaml"))
    ):
        try:
            raw = yaml.safe_load(m.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        name = raw.get("name")
        if isinstance(name, str):
            manifest_names.setdefault(name, []).append(_rel(m))

    details: list[str] = []
    failures = 0
    for digest, paths in bodies.items():
        if len(paths) > 1:
            failures += 1
            details.append(
                f"Duplicate body content (sha256={digest[:12]}…): "
                + ", ".join(paths)
            )

    warnings = 0
    for atom_id, paths in ids.items():
        if len(paths) > 1:
            warnings += 1
            details.append(
                f"Warning: duplicate frontmatter id '{atom_id}' in "
                + ", ".join(paths)
            )
    for name, paths in manifest_names.items():
        if len(paths) > 1:
            warnings += 1
            details.append(
                f"Warning: duplicate manifest name '{name}' in "
                + ", ".join(paths)
            )

    passed = failures == 0
    summary = f"{failures} duplicate(s), {warnings} warning(s)"
    return CheckResult("No duplicate atoms", passed, summary, details)


_AGENT_REQUIRED = ("agent.md", "manifest.yaml", "README.md")
_WORKFLOW_REQUIRED = ("flow.md", "manifest.yaml", "README.md")


def check_composite_completeness(root: Path) -> CheckResult:
    details: list[str] = []
    counts = {"agents": 0, "workflows": 0}

    agents = root / "agents"
    if agents.is_dir():
        for d in sorted(p for p in agents.iterdir() if p.is_dir()):
            counts["agents"] += 1
            missing = [
                f for f in _AGENT_REQUIRED if not (d / f).is_file()
            ]
            if missing:
                details.append(
                    f"{_rel(d)}: missing {', '.join(missing)}"
                )

    workflows = root / "workflows"
    if workflows.is_dir():
        for d in sorted(p for p in workflows.iterdir() if p.is_dir()):
            counts["workflows"] += 1
            missing = [
                f for f in _WORKFLOW_REQUIRED if not (d / f).is_file()
            ]
            if missing:
                details.append(
                    f"{_rel(d)}: missing {', '.join(missing)}"
                )

    passed = not details
    summary = (
        f"{counts['agents']} agent(s), {counts['workflows']} workflow(s)"
    )
    return CheckResult("Composite completeness", passed, summary, details)


def check_index_up_to_date(root: Path) -> CheckResult:
    placeholder, _failures = gi._build_placeholder_content(root)
    if not gi.INDEX_PATH.exists():
        return CheckResult(
            "Index up to date",
            False,
            "INDEX.md missing",
            ["INDEX.md does not exist; run generate_index.py"],
        )
    existing = gi.INDEX_PATH.read_text(encoding="utf-8")
    if gi._strip_timestamp(existing) != placeholder:
        return CheckResult(
            "Index up to date",
            False,
            "stale",
            ["INDEX.md is out of date; run generate_index.py"],
        )
    return CheckResult("Index up to date", True, "in sync", [])


# Naming-convention check ---------------------------------------------------


_KEBAB = re.compile(KEBAB_RE)
_SNAKE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
_NAMING_TARGETS = (
    "agents",
    "workflows",
    "skills",
    "prompts/library",
    "prompts/templates",
    "mcp-servers",
    "stack",
    "tools",
    "n8n-workflows",
)
# Files conventionally named outside the kebab-case rule. README.md is
# accepted scaffolding inside any folder; SKILL.md is the Anthropic skill
# manifest filename. ``.gitkeep`` is the standard empty-folder marker.
_NAMING_EXEMPT_BASENAMES = {"README.md", "SKILL.md", ".gitkeep"}


def _name_ok(parent_rel: str, entry: Path) -> bool:
    if entry.name in _NAMING_EXEMPT_BASENAMES:
        return True
    if entry.name.startswith("."):
        return True
    stem = entry.stem if entry.is_file() else entry.name
    # Python tooling lives in tools/ and follows Python conventions
    # (snake_case module names are required by the import system).
    if parent_rel == "tools" and entry.is_file() and entry.suffix == ".py":
        return bool(_SNAKE.match(stem))
    return bool(_KEBAB.match(stem))


def check_naming_conventions(root: Path) -> CheckResult:
    details: list[str] = []
    checked = 0
    for rel in _NAMING_TARGETS:
        parent = root / rel
        if not parent.is_dir():
            continue
        for entry in sorted(parent.iterdir()):
            if entry.name in _NAMING_EXEMPT_BASENAMES:
                continue
            if entry.name.startswith("."):
                continue
            # Generated Python artefacts (e.g. ``__pycache__``) are not
            # content; skip dunder-prefixed entries.
            if entry.name.startswith("__"):
                continue
            checked += 1
            if not _name_ok(rel, entry):
                details.append(
                    f"{rel}/{entry.name}: not kebab-case "
                    f"(stem must match {KEBAB_RE!r})"
                )
    passed = not details
    summary = f"{checked} entry name(s) checked"
    return CheckResult("Naming conventions", passed, summary, details)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _run_all(root: Path) -> list[CheckResult]:
    return [
        check_manifest_schema(root),
        check_frontmatter_schema(root),
        check_reference_schema_compliance(root),
        check_reference_subtype_folder_match(root),
        check_broken_references(root),
        check_no_duplicate_atoms(root),
        check_composite_completeness(root),
        check_index_up_to_date(root),
        check_naming_conventions(root),
    ]


def _render(results: list[CheckResult]) -> None:
    table = Table(title="Aithos Selection — Repository Check")
    table.add_column("Check", overflow="fold")
    table.add_column("Status", justify="center")
    table.add_column("Details", overflow="fold")
    for r in results:
        status = "[green]✓[/green]" if r.passed else "[red]✗ FAIL[/red]"
        table.add_row(r.name, status, r.summary)
    console.print(table)

    failed = [r for r in results if not r.passed]
    if failed:
        console.print()
        for r in failed:
            console.print(f"[red]✗ {r.name}[/red]")
            for line in r.details:
                console.print(f"  {line}")
        console.print()
        console.print(f"[red]{len(failed)} check(s) failed.[/red]")
    else:
        # If a passed check carries details (e.g. duplicate-id warnings),
        # surface them so the user notices.
        warning_blocks = [r for r in results if r.passed and r.details]
        if warning_blocks:
            console.print()
            for r in warning_blocks:
                console.print(f"[yellow]⚠ {r.name} — warnings[/yellow]")
                for line in r.details:
                    console.print(f"  {line}")
        console.print()
        console.print("[green]All checks passed.[/green]")


def _regenerate_index() -> None:
    placeholder, _ = gi._build_placeholder_content(ROOT)
    timestamp = gi._resolve_timestamp(placeholder, gi.INDEX_PATH)
    gi.INDEX_PATH.write_text(
        placeholder.replace(gi.TIMESTAMP_PLACEHOLDER, timestamp),
        encoding="utf-8",
    )


def main(
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Auto-fix safely fixable issues (currently: regenerate INDEX.md).",
    ),
) -> None:
    results = _run_all(ROOT)

    if fix:
        index_result = next(
            (r for r in results if r.name == "Index up to date"), None
        )
        if index_result and not index_result.passed:
            console.print("[yellow]Auto-fix: regenerating INDEX.md…[/yellow]")
            _regenerate_index()
            results = _run_all(ROOT)

    _render(results)
    if any(not r.passed for r in results):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
