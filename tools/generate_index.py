"""Generate INDEX.md for aithos-selection.

Walks the repository, parses frontmatter and manifests, and renders
INDEX.md. Idempotent: running twice yields byte-identical output, because
the "Last generated" timestamp is preserved when the surrounding content
has not changed.

CLI:
    uv run python tools/generate_index.py            # regenerate INDEX.md
    uv run python tools/generate_index.py --check    # exit 1 if stale

Discovery functions and the inverse-graph builder are imported by
``tools/check.py`` and must remain stable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional, Union

import typer
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError
from rich.console import Console

ROOT: Path = Path(__file__).resolve().parents[1]
INDEX_PATH: Path = ROOT / "INDEX.md"

console = Console()


# ---------------------------------------------------------------------------
# Schema models — mirror docs/schemas/{frontmatter,manifest}.schema.yaml
# ---------------------------------------------------------------------------


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AtomFrontmatter(_StrictModel):
    id: str
    name: str
    type: str
    status: str
    version: str
    description: str
    tags: list[str] = []
    language: str
    model: Optional[str] = None
    created: Union[date, str]
    updated: Union[date, str]
    author: str


class SkillFrontmatter(_StrictModel):
    """Anthropic skill format — only ``name`` and ``description`` are
    required, but other keys may appear and are tolerated."""

    model_config = ConfigDict(extra="allow")
    name: str
    description: str


class ReferenceFrontmatter(BaseModel):
    """Reference frontmatter — mirrors docs/schemas/reference.schema.yaml.

    Kept lenient (no regex / enum constraints) so discovery stays robust
    on mid-edit files. Strict validation lives in ``tools/check.py``.
    """

    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    type: str
    subtype: str
    url: str
    status: str
    description: str
    tags: list[str] = []
    language: str
    created: Union[date, str]
    updated: Union[date, str]
    author: str
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    github_stars: Optional[int] = None
    github_language: Optional[str] = None
    github_topics: list[str] = []
    github_last_commit: Optional[Union[date, str]] = None


class ManifestUses(_StrictModel):
    prompts: list[str] = []
    templates: list[str] = []
    mcp_servers: list[str] = []
    tools: list[str] = []


class Manifest(_StrictModel):
    name: str
    version: str
    type: str
    description: str
    status: str
    tags: list[str] = []
    created: Union[date, str]
    updated: Union[date, str]
    system_prompt: Optional[str] = None
    uses: Optional[ManifestUses] = None
    agents: list[str] = []
    n8n_workflows: list[str] = []


# ---------------------------------------------------------------------------
# Discovery dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Atom:
    kind: str
    path: str
    name: str
    status: str = ""
    tags: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class Composite:
    kind: str
    path: str
    name: str
    status: str
    tags: list[str]
    description: str
    uses_prompts: list[str] = field(default_factory=list)
    uses_templates: list[str] = field(default_factory=list)
    uses_mcp: list[str] = field(default_factory=list)
    uses_tools: list[str] = field(default_factory=list)
    system_prompt: str = ""


@dataclass
class Recipe:
    kind: str
    path: str
    name: str
    status: str
    tags: list[str]
    description: str
    agents: list[str] = field(default_factory=list)
    uses_prompts: list[str] = field(default_factory=list)
    uses_templates: list[str] = field(default_factory=list)
    uses_mcp: list[str] = field(default_factory=list)
    uses_tools: list[str] = field(default_factory=list)
    n8n_workflows: list[str] = field(default_factory=list)


@dataclass
class Reference:
    subtype: str
    path: str
    name: str
    url: str
    status: str
    tags: list[str]
    description: str
    id: str


@dataclass
class ParseFailure:
    path: str
    reason: str


# ---------------------------------------------------------------------------
# Frontmatter and YAML parsing helpers
# ---------------------------------------------------------------------------


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


def _read_frontmatter(p: Path) -> Optional[dict]:
    text = p.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    data = yaml.safe_load(m.group(1))
    return data or {}


def _rel(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


_ATOM_BUCKETS = (
    "prompt",
    "template",
    "stack-note",
    "skill",
    "mcp-config",
    "tool-script",
    "n8n-workflow",
)


def discover_atoms(root: Path) -> dict[str, list[Atom]]:
    """Discover all atom-shaped files in the repository.

    Returns a dict keyed by atom kind. Files that fail to parse are
    silently skipped here; use :func:`discover_atoms_with_failures` when
    you need the failure list (e.g. inside ``check.py``).
    """
    atoms, _ = discover_atoms_with_failures(root)
    return atoms


def discover_atoms_with_failures(
    root: Path,
) -> tuple[dict[str, list[Atom]], list[ParseFailure]]:
    failures: list[ParseFailure] = []
    out: dict[str, list[Atom]] = {k: [] for k in _ATOM_BUCKETS}

    def _push_frontmatter_atom(p: Path, bucket: str) -> None:
        try:
            fm = _read_frontmatter(p)
            if fm is None:
                failures.append(ParseFailure(_rel(p), "no frontmatter block"))
                return
            data = AtomFrontmatter(**fm)
            out[bucket].append(
                Atom(
                    kind=bucket,
                    path=_rel(p),
                    name=data.id,
                    status=data.status,
                    tags=list(data.tags),
                    description=data.description,
                )
            )
        except ValidationError as exc:
            failures.append(
                ParseFailure(_rel(p), f"schema: {exc.error_count()} error(s)")
            )
        except Exception as exc:  # pragma: no cover — defensive
            failures.append(
                ParseFailure(_rel(p), f"{type(exc).__name__}: {exc}")
            )

    # prompts/library/*.md (single-file) and prompts/library/*/README.md (folder-as-prompt)
    lib = root / "prompts" / "library"
    if lib.is_dir():
        for p in sorted(lib.glob("*.md")):
            if p.name == "README.md":
                continue
            _push_frontmatter_atom(p, "prompt")
        for d in sorted(p for p in lib.iterdir() if p.is_dir()):
            readme = d / "README.md"
            if readme.is_file():
                _push_frontmatter_atom(readme, "prompt")

    # prompts/templates/*.md
    tpl = root / "prompts" / "templates"
    if tpl.is_dir():
        for p in sorted(tpl.glob("*.md")):
            if p.name == "README.md":
                continue
            _push_frontmatter_atom(p, "template")

    # stack/*.md
    stack = root / "stack"
    if stack.is_dir():
        for p in sorted(stack.glob("*.md")):
            if p.name == "README.md":
                continue
            _push_frontmatter_atom(p, "stack-note")

    # skills/*/SKILL.md (Anthropic skill format)
    skills = root / "skills"
    if skills.is_dir():
        for skill_md in sorted(skills.glob("*/SKILL.md")):
            try:
                fm = _read_frontmatter(skill_md)
                if fm is None:
                    failures.append(
                        ParseFailure(_rel(skill_md), "no frontmatter block")
                    )
                    continue
                sk = SkillFrontmatter(**fm)
                out["skill"].append(
                    Atom(
                        kind="skill",
                        path=_rel(skill_md),
                        name=sk.name,
                        status="",
                        tags=[],
                        description=sk.description,
                    )
                )
            except ValidationError as exc:
                failures.append(
                    ParseFailure(
                        _rel(skill_md), f"schema: {exc.error_count()} error(s)"
                    )
                )
            except Exception as exc:  # pragma: no cover — defensive
                failures.append(
                    ParseFailure(_rel(skill_md), f"{type(exc).__name__}: {exc}")
                )

    # mcp-servers/*.json (+ optional companion .md)
    mcp_dir = root / "mcp-servers"
    if mcp_dir.is_dir():
        for p in sorted(mcp_dir.glob("*.json")):
            companion = p.with_suffix(".md")
            desc = ""
            status = ""
            tags: list[str] = []
            if companion.exists():
                try:
                    fm = _read_frontmatter(companion)
                    if fm:
                        data = AtomFrontmatter(**fm)
                        desc = data.description
                        status = data.status
                        tags = list(data.tags)
                except ValidationError as exc:
                    failures.append(
                        ParseFailure(
                            _rel(companion),
                            f"schema: {exc.error_count()} error(s)",
                        )
                    )
                except Exception as exc:  # pragma: no cover — defensive
                    failures.append(
                        ParseFailure(
                            _rel(companion), f"{type(exc).__name__}: {exc}"
                        )
                    )
            out["mcp-config"].append(
                Atom(
                    kind="mcp-config",
                    path=_rel(p),
                    name=p.stem,
                    status=status,
                    tags=tags,
                    description=desc,
                )
            )

    # tools/*.py (excluding generate_index.py and check.py from being indexed
    # as atoms? No — the spec lists tools/ as a generic catalog. Include all.)
    tools = root / "tools"
    if tools.is_dir():
        for p in sorted(tools.glob("*.py")):
            out["tool-script"].append(
                Atom(
                    kind="tool-script",
                    path=_rel(p),
                    name=p.stem,
                    description="",
                )
            )

    # n8n-workflows/*.json
    n8n = root / "n8n-workflows"
    if n8n.is_dir():
        for p in sorted(n8n.glob("*.json")):
            out["n8n-workflow"].append(
                Atom(
                    kind="n8n-workflow",
                    path=_rel(p),
                    name=p.stem,
                    description="",
                )
            )

    for bucket in out:
        out[bucket].sort(key=lambda a: (a.name, a.path))
    return out, failures


def discover_composites(root: Path) -> list[Composite]:
    composites, _ = discover_composites_with_failures(root)
    return composites


def discover_composites_with_failures(
    root: Path,
) -> tuple[list[Composite], list[ParseFailure]]:
    failures: list[ParseFailure] = []
    out: list[Composite] = []
    agents = root / "agents"
    if not agents.is_dir():
        return out, failures
    for m in sorted(agents.glob("*/manifest.yaml")):
        try:
            raw = yaml.safe_load(m.read_text(encoding="utf-8")) or {}
            data = Manifest(**raw)
            if data.type != "agent":
                failures.append(
                    ParseFailure(
                        _rel(m), f"expected type=agent, got {data.type!r}"
                    )
                )
                continue
            uses = data.uses or ManifestUses()
            out.append(
                Composite(
                    kind="agent",
                    path=_rel(m.parent),
                    name=data.name,
                    status=data.status,
                    tags=list(data.tags),
                    description=data.description,
                    uses_prompts=list(uses.prompts),
                    uses_templates=list(uses.templates),
                    uses_mcp=list(uses.mcp_servers),
                    uses_tools=list(uses.tools),
                    system_prompt=data.system_prompt or "",
                )
            )
        except ValidationError as exc:
            failures.append(
                ParseFailure(_rel(m), f"schema: {exc.error_count()} error(s)")
            )
        except Exception as exc:  # pragma: no cover — defensive
            failures.append(
                ParseFailure(_rel(m), f"{type(exc).__name__}: {exc}")
            )
    out.sort(key=lambda c: (c.name, c.path))
    return out, failures


def discover_recipes(root: Path) -> list[Recipe]:
    recipes, _ = discover_recipes_with_failures(root)
    return recipes


def discover_recipes_with_failures(
    root: Path,
) -> tuple[list[Recipe], list[ParseFailure]]:
    failures: list[ParseFailure] = []
    out: list[Recipe] = []
    workflows = root / "workflows"
    if not workflows.is_dir():
        return out, failures
    for m in sorted(workflows.glob("*/manifest.yaml")):
        try:
            raw = yaml.safe_load(m.read_text(encoding="utf-8")) or {}
            data = Manifest(**raw)
            if data.type != "workflow":
                failures.append(
                    ParseFailure(
                        _rel(m), f"expected type=workflow, got {data.type!r}"
                    )
                )
                continue
            uses = data.uses or ManifestUses()
            out.append(
                Recipe(
                    kind="workflow",
                    path=_rel(m.parent),
                    name=data.name,
                    status=data.status,
                    tags=list(data.tags),
                    description=data.description,
                    agents=list(data.agents),
                    uses_prompts=list(uses.prompts),
                    uses_templates=list(uses.templates),
                    uses_mcp=list(uses.mcp_servers),
                    uses_tools=list(uses.tools),
                    n8n_workflows=list(data.n8n_workflows),
                )
            )
        except ValidationError as exc:
            failures.append(
                ParseFailure(_rel(m), f"schema: {exc.error_count()} error(s)")
            )
        except Exception as exc:  # pragma: no cover — defensive
            failures.append(
                ParseFailure(_rel(m), f"{type(exc).__name__}: {exc}")
            )
    out.sort(key=lambda r: (r.name, r.path))
    return out, failures


_REFERENCE_SUBTYPES = ("repo", "article", "template")
_REFERENCE_SUBTYPE_FROM_FOLDER = {
    "repos": "repo",
    "articles": "article",
    "templates": "template",
}


def discover_references(root: Path) -> dict[str, list[Reference]]:
    """Discover all reference Markdown files grouped by subtype.

    Walks ``references/<subtype-folder>/*.md`` (skipping README.md). The
    result is keyed by subtype (``repo``, ``article``, ``template``).
    Files that fail to parse are silently skipped here; use
    :func:`discover_references_with_failures` when you need the failure
    list (e.g. inside ``check.py``).
    """
    refs, _ = discover_references_with_failures(root)
    return refs


def discover_references_with_failures(
    root: Path,
) -> tuple[dict[str, list[Reference]], list[ParseFailure]]:
    failures: list[ParseFailure] = []
    out: dict[str, list[Reference]] = {k: [] for k in _REFERENCE_SUBTYPES}
    refs_root = root / "references"
    if not refs_root.is_dir():
        return out, failures

    for folder_name, subtype in _REFERENCE_SUBTYPE_FROM_FOLDER.items():
        sub = refs_root / folder_name
        if not sub.is_dir():
            continue
        for p in sorted(sub.glob("*.md")):
            if p.name == "README.md":
                continue
            try:
                fm = _read_frontmatter(p)
                if fm is None:
                    failures.append(
                        ParseFailure(_rel(p), "no frontmatter block")
                    )
                    continue
                data = ReferenceFrontmatter(**fm)
                out[subtype].append(
                    Reference(
                        subtype=data.subtype,
                        path=_rel(p),
                        name=data.name,
                        url=data.url,
                        status=data.status,
                        tags=list(data.tags),
                        description=data.description,
                        id=data.id,
                    )
                )
            except ValidationError as exc:
                failures.append(
                    ParseFailure(
                        _rel(p), f"schema: {exc.error_count()} error(s)"
                    )
                )
            except Exception as exc:  # pragma: no cover — defensive
                failures.append(
                    ParseFailure(_rel(p), f"{type(exc).__name__}: {exc}")
                )

    for subtype in out:
        out[subtype].sort(key=lambda r: (r.id, r.path))
    return out, failures


def build_inverse_graph(
    atoms: dict[str, list[Atom]],
    composites: list[Composite],
    recipes: list[Recipe],
) -> dict[str, list[str]]:
    """Map every discovered atom path to the composites/recipes that
    reference it. Atom paths that no manifest references end up with an
    empty list (these are the orphans)."""
    graph: dict[str, list[str]] = {}
    for bucket in atoms.values():
        for a in bucket:
            graph.setdefault(a.path, [])

    def _record(atom_path: str, user_path: str) -> None:
        if atom_path in graph and user_path not in graph[atom_path]:
            graph[atom_path].append(user_path)

    for c in composites:
        for paths in (
            c.uses_prompts,
            c.uses_templates,
            c.uses_mcp,
            c.uses_tools,
        ):
            for p in paths:
                _record(p, c.path)
    for r in recipes:
        for paths in (
            r.uses_prompts,
            r.uses_templates,
            r.uses_mcp,
            r.uses_tools,
            r.n8n_workflows,
        ):
            for p in paths:
                _record(p, r.path)

    for k in graph:
        graph[k] = sorted(graph[k])
    return graph


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


DESC_TRUNCATE = 60
EMPTY_LINE = "_No items yet._"


def _trunc(s: str, n: int = DESC_TRUNCATE) -> str:
    s = (s or "").replace("\n", " ").strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rstrip() + "…"


def _esc(s: str) -> str:
    return (s or "").replace("|", "\\|")


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return EMPTY_LINE
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join("---" for _ in headers) + "|"
    body_lines = [
        "| " + " | ".join(_esc(c) for c in row) + " |" for row in rows
    ]
    return "\n".join([header_line, sep_line, *body_lines])


def render_index(
    atoms: dict[str, list[Atom]],
    composites: list[Composite],
    recipes: list[Recipe],
    graph: dict[str, list[str]],
    timestamp: str,
    references: Optional[dict[str, list[Reference]]] = None,
) -> str:
    """Render the full INDEX.md contents (including the given timestamp)."""
    parts: list[str] = []

    parts.append("# Aithos Selection — Index")
    parts.append("")
    parts.append(
        "_Auto-generated by `tools/generate_index.py`. Do not edit by hand._"
    )
    parts.append("")
    parts.append(f"_Last generated: {timestamp}_")
    parts.append("")

    # ---- Atoms ----
    parts.append("## Atoms")
    parts.append("")

    parts.append("### Prompts (library)")
    parts.append("")
    parts.append(
        _table(
            ["ID", "Status", "Tags", "Description"],
            [
                [a.name, a.status, ", ".join(a.tags), _trunc(a.description)]
                for a in atoms["prompt"]
            ],
        )
    )
    parts.append("")

    parts.append("### Prompts (templates)")
    parts.append("")
    parts.append(
        _table(
            ["ID", "Status", "Tags", "Description"],
            [
                [a.name, a.status, ", ".join(a.tags), _trunc(a.description)]
                for a in atoms["template"]
            ],
        )
    )
    parts.append("")

    parts.append("### MCP servers")
    parts.append("")
    parts.append(
        _table(
            ["Name", "Status", "Tags", "Description"],
            [
                [a.name, a.status, ", ".join(a.tags), _trunc(a.description)]
                for a in atoms["mcp-config"]
            ],
        )
    )
    parts.append("")

    parts.append("### Tools")
    parts.append("")
    parts.append(
        _table(
            ["Name", "Path"],
            [[a.name, a.path] for a in atoms["tool-script"]],
        )
    )
    parts.append("")

    parts.append("### Stack notes")
    parts.append("")
    parts.append(
        _table(
            ["ID", "Status", "Tags", "Description"],
            [
                [a.name, a.status, ", ".join(a.tags), _trunc(a.description)]
                for a in atoms["stack-note"]
            ],
        )
    )
    parts.append("")

    parts.append("### Skills")
    parts.append("")
    parts.append(
        _table(
            ["Name", "Description"],
            [[a.name, _trunc(a.description)] for a in atoms["skill"]],
        )
    )
    parts.append("")

    # ---- Composites ----
    parts.append("## Composites")
    parts.append("")
    parts.append("### Agents")
    parts.append("")
    parts.append(
        _table(
            ["Name", "Status", "Uses", "Description"],
            [
                [
                    c.name,
                    c.status,
                    (
                        f"prompts: {len(c.uses_prompts)}, "
                        f"templates: {len(c.uses_templates)}, "
                        f"mcp: {len(c.uses_mcp)}, "
                        f"tools: {len(c.uses_tools)}"
                    ),
                    _trunc(c.description),
                ]
                for c in composites
            ],
        )
    )
    parts.append("")

    # ---- Recipes ----
    parts.append("## Recipes")
    parts.append("")
    parts.append("### Workflows")
    parts.append("")
    parts.append(
        _table(
            ["Name", "Status", "Uses", "Description"],
            [
                [
                    r.name,
                    r.status,
                    f"agents: {len(r.agents)}, n8n: {len(r.n8n_workflows)}",
                    _trunc(r.description),
                ]
                for r in recipes
            ],
        )
    )
    parts.append("")

    parts.append("### Standalone n8n workflows")
    parts.append("")
    parts.append(
        _table(
            ["Name", "Path"],
            [[a.name, a.path] for a in atoms["n8n-workflow"]],
        )
    )
    parts.append("")

    # ---- References ----
    refs = references or {k: [] for k in _REFERENCE_SUBTYPES}
    parts.append("## References")
    parts.append("")

    def _reference_rows(subtype: str) -> list[list[str]]:
        return [
            [
                r.id,
                r.url,
                r.status,
                ", ".join(r.tags),
                _trunc(r.description),
            ]
            for r in refs.get(subtype, [])
        ]

    parts.append("### Repos")
    parts.append("")
    parts.append(
        _table(
            ["Name", "URL", "Status", "Tags", "Description"],
            _reference_rows("repo"),
        )
    )
    parts.append("")

    parts.append("### Articles")
    parts.append("")
    parts.append(
        _table(
            ["Name", "URL", "Status", "Tags", "Description"],
            _reference_rows("article"),
        )
    )
    parts.append("")

    parts.append("### Templates")
    parts.append("")
    parts.append(
        _table(
            ["Name", "URL", "Status", "Tags", "Description"],
            _reference_rows("template"),
        )
    )
    parts.append("")

    # ---- Inverse graph ----
    parts.append("## Inverse dependency graph")
    parts.append("")
    parts.append("### Which composites/recipes use each atom?")
    parts.append("")
    used_rows = [
        [atom_path, ", ".join(users)]
        for atom_path, users in sorted(graph.items())
        if users
    ]
    parts.append(_table(["Atom", "Used by"], used_rows))
    parts.append("")

    parts.append("### Orphan atoms (not used by any composite/recipe)")
    parts.append("")
    orphans = sorted(p for p, users in graph.items() if not users)
    if orphans:
        for p in orphans:
            parts.append(f"- `{p}`")
    else:
        parts.append("- _None_")
    parts.append("")

    return "\n".join(parts).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Idempotency: preserve timestamp when content hasn't changed
# ---------------------------------------------------------------------------


TIMESTAMP_PLACEHOLDER = "__TIMESTAMP__"
TIMESTAMP_LINE_RE = re.compile(r"_Last generated: [^_\n]+_")


def _strip_timestamp(content: str) -> str:
    return TIMESTAMP_LINE_RE.sub(
        f"_Last generated: {TIMESTAMP_PLACEHOLDER}_", content
    )


def _extract_timestamp(content: str) -> Optional[str]:
    m = TIMESTAMP_LINE_RE.search(content)
    if not m:
        return None
    inner = m.group()[len("_Last generated: ") : -1]
    return inner if inner and inner != TIMESTAMP_PLACEHOLDER else None


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_placeholder_content(
    root: Path,
) -> tuple[str, list[ParseFailure]]:
    atoms, fa = discover_atoms_with_failures(root)
    composites, fc = discover_composites_with_failures(root)
    recipes, fr = discover_recipes_with_failures(root)
    references, fref = discover_references_with_failures(root)
    graph = build_inverse_graph(atoms, composites, recipes)
    content = render_index(
        atoms,
        composites,
        recipes,
        graph,
        TIMESTAMP_PLACEHOLDER,
        references=references,
    )
    return content, fa + fc + fr + fref


def _resolve_timestamp(placeholder_content: str, existing_path: Path) -> str:
    if existing_path.exists():
        existing = existing_path.read_text(encoding="utf-8")
        if _strip_timestamp(existing) == placeholder_content:
            ts = _extract_timestamp(existing)
            if ts:
                return ts
    return _now_iso_utc()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _report_failures(failures: list[ParseFailure], header: str) -> None:
    if not failures:
        return
    console.print(f"[yellow]{header}[/yellow]")
    for f in failures:
        console.print(f"  - {f.path}: {f.reason}")


def main(
    check: bool = typer.Option(
        False,
        "--check",
        help="Exit non-zero if INDEX.md is out of date. Used in CI.",
    ),
) -> None:
    placeholder_content, failures = _build_placeholder_content(ROOT)
    timestamp = _resolve_timestamp(placeholder_content, INDEX_PATH)
    new_content = placeholder_content.replace(
        TIMESTAMP_PLACEHOLDER, timestamp
    )

    if check:
        if not INDEX_PATH.exists():
            console.print(
                "[red]INDEX.md does not exist.[/red] "
                "Run: uv run python tools/generate_index.py"
            )
            raise typer.Exit(code=1)
        existing = INDEX_PATH.read_text(encoding="utf-8")
        if _strip_timestamp(existing) != placeholder_content:
            console.print(
                "[red]INDEX.md is out of date.[/red] "
                "Run: uv run python tools/generate_index.py"
            )
            _report_failures(failures, "Files that failed to parse:")
            raise typer.Exit(code=1)
        console.print("[green]INDEX.md is up to date.[/green]")
        _report_failures(failures, "Files that failed to parse:")
        return

    INDEX_PATH.write_text(new_content, encoding="utf-8")
    rel = INDEX_PATH.relative_to(ROOT)
    console.print(f"[green]Wrote {rel}[/green] (timestamp: {timestamp})")
    _report_failures(failures, "Files that failed to parse (skipped):")


if __name__ == "__main__":
    typer.run(main)
