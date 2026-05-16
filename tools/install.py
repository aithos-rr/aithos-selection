"""Install skills and subagents from this curated library to their
runtime locations.

Without this tool, ``skills/<name>/`` and ``subagents/<name>/`` are pure
catalog entries that Claude Code does not see. ``install.py`` bridges
that gap by symlinking (default) or copying each item into the user's
runtime tree:

- **skills** → ``~/.claude/skills/<name>`` by default.
- **subagents** → require an explicit ``--target`` (project-specific
  ``.claude/agents/``).

The install log at ``~/.aithos-install-log.yaml`` records every
deployment, enabling ``list`` and ``uninstall``.

CLI:

    uv run python tools/install.py install skills/librarian
    uv run python tools/install.py install subagents/foo --target ~/myproj/.claude/agents/foo
    uv run python tools/install.py list
    uv run python tools/install.py info skills/librarian
    uv run python tools/install.py uninstall librarian

Exit codes:

- 0 success
- 1 generic / unexpected exception
- 2 invalid arguments (e.g. subagent without ``--target``)
- 3 target collision without ``--force``
- 4 ambiguous uninstall (multiple matches, non-interactive)
- 5 source not found / not a valid skill or subagent
- 6 log file corrupt or unreadable
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    add_completion=False,
    help="Deploy skills and subagents from this library to runtime targets.",
)

console = Console()
err_console = Console(stderr=True)

ROOT: Path = Path(__file__).resolve().parents[1]
LOG_PATH: Path = Path.home() / ".aithos-install-log.yaml"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


# ---------------------------------------------------------------------------
# Errors and exit helpers
# ---------------------------------------------------------------------------


def _error(msg: str, code: int) -> "typer.Exit":
    err_console.print(f"[red]Error:[/red] {msg}")
    return typer.Exit(code=code)


# ---------------------------------------------------------------------------
# Log file — atomic read/write
# ---------------------------------------------------------------------------


def _load_log() -> dict:
    if not LOG_PATH.exists():
        return {"installs": []}
    try:
        data = yaml.safe_load(LOG_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise _error(
            f"install log {LOG_PATH} is unreadable: {exc}", 6
        )
    if data is None:
        return {"installs": []}
    if not isinstance(data, dict) or not isinstance(
        data.get("installs"), list
    ):
        raise _error(
            f"install log {LOG_PATH} has unexpected shape (expected "
            f"top-level 'installs' list)",
            6,
        )
    return data


def _save_log(data: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = LOG_PATH.with_suffix(".yaml.tmp")
    tmp.write_text(
        yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    os.replace(tmp, LOG_PATH)


# ---------------------------------------------------------------------------
# Source resolution and classification
# ---------------------------------------------------------------------------


def _resolve_source(item_path: str) -> Path:
    """Resolve ``item_path`` to an absolute directory inside this repo.

    Accepts relative paths (resolved against the current working
    directory) and absolute paths. Returns the canonical resolved
    ``Path``. Does not classify; classification is done by
    :func:`_classify_source`.
    """
    p = Path(item_path)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p.resolve()


def _classify_source(src: Path) -> str:
    """Return ``"skill"`` or ``"subagent"`` for a valid source path,
    raising ``typer.Exit(5)`` otherwise."""
    if not src.is_dir():
        raise _error(
            f"source {src} does not exist or is not a directory", 5
        )
    parent_name = src.parent.name
    if parent_name == "skills":
        skill_md = src / "SKILL.md"
        if not skill_md.is_file():
            raise _error(
                f"source {src} is under skills/ but does not contain "
                f"SKILL.md",
                5,
            )
        return "skill"
    if parent_name == "subagents":
        manifest = src / "manifest.yaml"
        if not manifest.is_file():
            raise _error(
                f"source {src} is under subagents/ but does not contain "
                f"manifest.yaml",
                5,
            )
        try:
            manifest_data = (
                yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
            )
        except yaml.YAMLError as exc:
            raise _error(f"subagent manifest unreadable: {exc}", 5)
        entry = manifest_data.get("entrypoint")
        if not isinstance(entry, str) or not entry:
            raise _error(
                f"subagent manifest {manifest} has no 'entrypoint' field",
                5,
            )
        target = (manifest.parent / entry).resolve()
        if not target.is_file():
            raise _error(
                f"subagent entrypoint {entry!r} does not resolve to a "
                f"file inside {src}",
                5,
            )
        return "subagent"
    raise _error(
        f"source {src} is neither under skills/ nor subagents/ — cannot "
        f"classify",
        5,
    )


def _read_frontmatter(p: Path) -> Optional[dict]:
    text = p.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    data = yaml.safe_load(m.group(1))
    return data or {}


def _read_metadata(src: Path, kind: str) -> dict:
    """Return a dict of metadata for printing in ``info``."""
    if kind == "skill":
        fm = _read_frontmatter(src / "SKILL.md") or {}
        return {
            "name": fm.get("name", src.name),
            "type": "skill",
            "description": fm.get("description", ""),
            "version": fm.get("version", ""),
            "raw_frontmatter": fm,
        }
    manifest = (
        yaml.safe_load((src / "manifest.yaml").read_text(encoding="utf-8"))
        or {}
    )
    return {
        "name": manifest.get("name", src.name),
        "type": "subagent",
        "description": manifest.get("description", ""),
        "version": manifest.get("version", ""),
        "status": manifest.get("status", ""),
        "tags": manifest.get("tags", []) or [],
        "tools": manifest.get("tools", []) or [],
        "mcp_servers": manifest.get("mcp_servers", []) or [],
        "skills_dependencies": manifest.get("skills_dependencies", []) or [],
        "origin": manifest.get("origin", {}),
        "raw_manifest": manifest,
    }


# ---------------------------------------------------------------------------
# Target handling
# ---------------------------------------------------------------------------


def _default_target(kind: str, name: str) -> Path:
    if kind == "skill":
        return Path.home() / ".claude" / "skills" / name
    # subagents have no default
    raise _error(
        f"{kind}s require an explicit --target (they belong to a "
        f"specific project's .claude/agents/, not a global location)",
        2,
    )


def _resolve_target(target: Optional[str], kind: str, name: str) -> Path:
    if target is None:
        return _default_target(kind, name)
    p = Path(target).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    return p.resolve()


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_same_symlink(target: Path, source: Path) -> bool:
    if not target.is_symlink():
        return False
    try:
        link = os.readlink(target)
    except OSError:
        return False
    return Path(link) == source


def _remove_target(target: Path) -> None:
    """Remove ``target`` regardless of whether it's a symlink, directory,
    or regular file. Caller is responsible for confirming intent (e.g.
    via ``--force``)."""
    if target.is_symlink():
        target.unlink()
        return
    if target.is_dir():
        shutil.rmtree(target)
        return
    if target.exists():
        target.unlink()


@app.command(help="Install a skill or subagent to its runtime location.")
def install(
    item_path: str = typer.Argument(
        ...,
        help=(
            "Path to the item (relative to cwd or absolute). Must be "
            "under skills/<name> or subagents/<name>."
        ),
    ),
    target: Optional[str] = typer.Option(
        None,
        "--target",
        help=(
            "Destination directory. Defaults to ~/.claude/skills/<name> "
            "for skills; required for subagents."
        ),
    ),
    mode: str = typer.Option(
        "symlink",
        "--mode",
        help="Deployment mode: 'symlink' (default) or 'copy'.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="If the target exists, remove it before deploying.",
    ),
) -> None:
    if mode not in ("symlink", "copy"):
        raise _error(f"--mode must be 'symlink' or 'copy', got {mode!r}", 2)

    src = _resolve_source(item_path)
    kind = _classify_source(src)
    name = src.name

    dst = _resolve_target(target, kind, name)

    log = _load_log()
    existing_entry = next(
        (
            e
            for e in log["installs"]
            if e.get("target") == str(dst) and e.get("source") == str(src)
        ),
        None,
    )

    # Idempotency: same source already installed to same target in the
    # same mode, and the deployment artifact still exists.
    if existing_entry and not force:
        same_mode = existing_entry.get("mode") == mode
        deployment_ok = (
            dst.is_symlink() and _is_same_symlink(dst, src)
            if mode == "symlink"
            else dst.is_dir()
        )
        if same_mode and deployment_ok:
            console.print(
                f"Already installed at [bold]{dst}[/bold] "
                f"(mode={mode}). Use --force to reinstall."
            )
            return

    if dst.exists() or dst.is_symlink():
        if not force:
            raise _error(
                f"target {dst} already exists. Use --force to replace it.",
                3,
            )
        if dst.is_file() and not dst.is_symlink():
            # Spec: refuse to clobber a regular file even with --force,
            # because that's almost certainly user data.
            raise _error(
                f"target {dst} is a regular file (not a symlink or "
                f"directory); refusing to clobber even with --force",
                3,
            )
        _remove_target(dst)

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        if mode == "symlink":
            os.symlink(src, dst)
        else:  # copy
            shutil.copytree(src, dst, symlinks=False)
    except OSError as exc:
        hint = ""
        if mode == "symlink":
            hint = " (try --mode copy if symlinks are not supported here)"
        raise _error(f"deployment failed: {exc}{hint}", 1)

    # Update log: drop any prior entry for the same target (force-replace
    # case), then append the new one.
    log["installs"] = [
        e for e in log["installs"] if e.get("target") != str(dst)
    ]
    log["installs"].append(
        {
            "name": name,
            "type": kind,
            "source": str(src),
            "target": str(dst),
            "mode": mode,
            "installed": _now_iso_utc(),
        }
    )
    _save_log(log)

    console.print(
        f"[green]✓[/green] Installed [bold]{name}[/bold] to {dst} "
        f"(mode={mode})"
    )


# ---------------------------------------------------------------------------
# uninstall
# ---------------------------------------------------------------------------


@app.command(help="Uninstall a previously installed skill or subagent.")
def uninstall(
    name_or_target: str = typer.Argument(
        ...,
        help=(
            "Item name (kebab-case) or full path of an installed target."
        ),
    ),
) -> None:
    log = _load_log()
    looks_like_path = (
        "/" in name_or_target
        or name_or_target.startswith("~")
        or Path(name_or_target).is_absolute()
    )

    if looks_like_path:
        resolved = str(
            Path(name_or_target).expanduser().resolve(strict=False)
        )
        matches = [
            e for e in log["installs"] if e.get("target") == resolved
        ]
    else:
        matches = [
            e for e in log["installs"] if e.get("name") == name_or_target
        ]

    if not matches:
        raise _error(
            f"no installs match {name_or_target!r}. Run "
            f"'install.py list' to see what's installed.",
            5,
        )

    if len(matches) > 1:
        # Multiple — disambiguate. Interactive prompt if stdin is a TTY.
        console.print(
            f"Multiple matches for {name_or_target!r}:"
        )
        for i, e in enumerate(matches, 1):
            console.print(
                f"  [{i}] {e['target']}  (mode={e['mode']}, "
                f"installed={e['installed']})"
            )
        if not sys.stdin.isatty():
            raise _error(
                "ambiguous uninstall (non-interactive). Re-run with the "
                "full target path to disambiguate.",
                4,
            )
        choice = typer.prompt(
            "Which one to uninstall? (number, or 'all')", default=""
        )
        if choice.strip().lower() == "all":
            selected = matches
        else:
            try:
                idx = int(choice.strip())
            except ValueError:
                raise _error(f"invalid choice {choice!r}", 4)
            if not 1 <= idx <= len(matches):
                raise _error(f"choice {idx} out of range", 4)
            selected = [matches[idx - 1]]
    else:
        selected = matches

    selected_targets = {e["target"] for e in selected}
    for entry in selected:
        target_path = Path(entry["target"])
        if target_path.exists() or target_path.is_symlink():
            _remove_target(target_path)
        console.print(
            f"[green]✓[/green] Uninstalled [bold]{entry['name']}[/bold] "
            f"from {entry['target']}"
        )

    log["installs"] = [
        e for e in log["installs"] if e.get("target") not in selected_targets
    ]
    _save_log(log)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@app.command("list", help="List all currently installed items.")
def list_installs() -> None:
    log = _load_log()
    entries = log["installs"]
    if not entries:
        console.print("No items installed.")
        return

    any_missing = any(
        not (
            Path(e["target"]).exists() or Path(e["target"]).is_symlink()
        )
        for e in entries
    )

    table = Table(title="Aithos Selection — Installed items")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Target", overflow="fold")
    table.add_column("Mode")
    table.add_column("Installed")
    if any_missing:
        table.add_column("Status")

    for entry in entries:
        target_path = Path(entry["target"])
        missing = not (target_path.exists() or target_path.is_symlink())
        name_cell = (
            f"{'⚠️ ' if missing else ''}{entry.get('name', '')}"
        )
        row = [
            name_cell,
            entry.get("type", ""),
            entry.get("target", ""),
            entry.get("mode", ""),
            entry.get("installed", ""),
        ]
        if any_missing:
            row.append("missing" if missing else "ok")
        table.add_row(*row)

    console.print(table)


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


@app.command(help="Show metadata about a library item without installing.")
def info(
    item_path: str = typer.Argument(
        ...,
        help=(
            "Path to the item (relative to cwd or absolute). Must be "
            "under skills/<name> or subagents/<name>."
        ),
    ),
) -> None:
    src = _resolve_source(item_path)
    kind = _classify_source(src)
    meta = _read_metadata(src, kind)

    console.print(f"[bold]{meta['name']}[/bold]  ({meta['type']})")
    if meta.get("version"):
        console.print(f"  version:     {meta['version']}")
    if kind == "subagent" and meta.get("status"):
        console.print(f"  status:      {meta['status']}")
    if meta.get("description"):
        console.print(f"  description: {meta['description']}")
    if kind == "subagent":
        tags = meta.get("tags") or []
        if tags:
            console.print(f"  tags:        {', '.join(tags)}")
        origin = meta.get("origin") or {}
        if isinstance(origin, dict) and origin.get("source"):
            console.print(f"  origin:      {origin['source']}")
        tools = meta.get("tools") or []
        if tools:
            console.print(
                f"  tools:       {', '.join(tools)} "
                f"({len(tools)})"
            )
        mcp = meta.get("mcp_servers") or []
        if mcp:
            console.print(
                f"  mcp_servers: {', '.join(mcp)} ({len(mcp)})"
            )
        skills = meta.get("skills_dependencies") or []
        if skills:
            console.print(
                f"  skills_dependencies: {', '.join(skills)} "
                f"({len(skills)})"
            )


if __name__ == "__main__":
    app()
