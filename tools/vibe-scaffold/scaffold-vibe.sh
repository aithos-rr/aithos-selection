#!/usr/bin/env bash
# ============================================================
# scaffold-vibe.sh — AI-Lab vibe-coding project scaffolder
# Canonical source: _assets-repos/tools/vibe-scaffold/
# Called via the `vibeproj` function in ~/.bashrc
# ============================================================
set -euo pipefail

VIBE_ROOT="${VIBE_ROOT:-$HOME/vibe-projects}"
SKILLS_SRC="${SKILLS_SRC:-$HOME/vibe-projects/_skills}"
DEFAULT_SKILLS=("use-railway" "prd-architect" "find-skills")
TEMPLATES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/templates" && pwd)"

usage() { echo "Usage: vibeproj <project-name> [--no-open]"; exit 1; }

[ $# -ge 1 ] || usage
NAME="$1"
OPEN_VSCODE=true
[ "${2:-}" = "--no-open" ] && OPEN_VSCODE=false

# --- Validations (001-policy: kebab-case, lowercase, english) ---
if ! [[ "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: name must be lowercase kebab-case (e.g. my-new-project)" >&2; exit 1
fi

PROJECT_DIR="$VIBE_ROOT/$NAME"
if [ -e "$PROJECT_DIR" ]; then
  echo "ERROR: project already exists: $PROJECT_DIR" >&2; exit 1
fi
if [ ! -d "$SKILLS_SRC" ]; then
  echo "ERROR: skills source not found: $SKILLS_SRC" >&2
  echo "Create it and add skills (e.g. use-railway, prd-architect) first." >&2; exit 1
fi

echo "▸ Creating $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"/{progress,src,.claude/skills,.claude/commands}

# --- Templates ---
cp -r "$TEMPLATES_DIR/devcontainer" "$PROJECT_DIR/.devcontainer"
cp "$TEMPLATES_DIR"/{CLAUDE.md,PRD.md,TASKS.md,PROMPT.md,loop.sh} "$PROJECT_DIR/"
cp "$TEMPLATES_DIR/commands/prd.md" "$PROJECT_DIR/.claude/commands/prd.md"
cp "$TEMPLATES_DIR/gitignore-template" "$PROJECT_DIR/.gitignore"
chmod +x "$PROJECT_DIR/loop.sh"

# Inject project name
sed -i "s/{{PROJECT_NAME}}/$NAME/g" "$PROJECT_DIR"/{CLAUDE.md,PRD.md,TASKS.md}
printf '# %s\n\nVibe project initialized %s. See CLAUDE.md for the operating protocol.\n' \
  "$NAME" "$(date +%F)" > "$PROJECT_DIR/README.md"
touch "$PROJECT_DIR/progress/log.md" "$PROJECT_DIR/.env"

# --- Skills: symlinks to /skills (mounted in the devcontainer from $SKILLS_SRC) ---
for skill in "${DEFAULT_SKILLS[@]}"; do
  if [ -d "$SKILLS_SRC/$skill" ]; then
    ln -sfn "/skills/$skill" "$PROJECT_DIR/.claude/skills/$skill"
    echo "▸ Linked skill: $skill"
  else
    echo "⚠ Skill not found in source, skipped: $skill"
  fi
done

# --- Git ---
git -C "$PROJECT_DIR" init -b main -q
git -C "$PROJECT_DIR" add -A
git -C "$PROJECT_DIR" commit -q -m "initial commit: vibe scaffold" --no-verify

echo ""
echo "✔ Project ready: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "  1. code $PROJECT_DIR            (then: 'Reopen in Container')"
echo "  2. In the container terminal:   claude   →  /prd   (build the PRD interactively)"
echo "  3. Launch the autonomous loop:  ./loop.sh [max-iterations]"
echo ""
echo "Skill management (per project):"
echo "  add:    ln -sfn /skills/<name> .claude/skills/<name>"
echo "  remove: rm .claude/skills/<name>"
echo "  source: $SKILLS_SRC  (populate via 'npx skills add <skill>' or git)"

if $OPEN_VSCODE && command -v code >/dev/null 2>&1; then
  code "$PROJECT_DIR"
fi
