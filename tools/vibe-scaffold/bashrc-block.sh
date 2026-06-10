# ============================================================
# AI-Lab — Vibe coding (bash launcher)
# Logic lives in ~/projects/aithos-selection/tools/vibe-scaffold/ (canonical, versioned)
# ============================================================
export VIBE_ROOT="$HOME/vibe-projects"
export SKILLS_SRC="$HOME/vibe-projects/_skills"
VIBE_SCAFFOLD="$HOME/projects/aithos-selection/tools/vibe-scaffold/scaffold-vibe.sh"

vibeproj() { bash "$VIBE_SCAFFOLD" "$@"; }
vibe()     { cd "$VIBE_ROOT"; }

# Railway: account token creato una volta su railway.com → Account Settings → Tokens.
# Viene iniettato automaticamente in ogni devcontainer (zero login per progetto).
export RAILWAY_API_TOKEN="INCOLLA-QUI-IL-TUO-TOKEN"

# SSH agent: VS Code lo inoltra automaticamente nei devcontainer → push GitHub
# funziona ovunque senza registrazioni. Avvio automatico se non attivo:
if [ -z "${SSH_AUTH_SOCK:-}" ]; then
  eval "$(ssh-agent -s)" > /dev/null
  ssh-add ~/.ssh/id_ed25519 2>/dev/null || true
fi
