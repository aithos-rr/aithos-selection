# vibe-scaffold

Scaffolder AI-Lab per progetti vibe-coding autonomi: devcontainer ufficiale Anthropic
(sandbox + firewall), Ralph loop fresh-context, skills via symlink, Railway CLI integrata.
Documentazione completa: `home/knowledge/_docs/006-vibe-coding-stack.md`.

## Installazione (una volta sola)

```bash
# 1. Sorgente canonica scaffolder (versionata), nel repo asset su Linux:
#    unzip del pacchetto in ~/projects/aithos-selection/tools/vibe-scaffold/
#    poi commit + push del repo

# 2. Sorgente canonica skills (ext4, montata in ogni container su /skills):
mkdir -p ~/vibe-projects/_skills
cp -r skills/use-railway skills/prd-architect skills/find-skills ~/vibe-projects/_skills/
cd ~/vibe-projects/_skills && git init -b main && git add -A && git commit -m "init: vibe skills"

# 3. Launcher bash:
cat bashrc-block.sh >> ~/.bashrc
#    → aprire ~/.bashrc e incollare il proprio RAILWAY_API_TOKEN
source ~/.bashrc
#    Se usi zsh come shell di default: cat bashrc-block.sh >> ~/.zshrc
```

## Autenticazioni (una volta sola, NON per progetto)

| CLI | Setup | Persistenza |
|---|---|---|
| Claude Code | `claude` → login al primo container | volume Docker condiviso `claude-code-config-vibe` |
| Railway | token in `~/.bashrc` (vedi sopra) | iniettato in ogni container via env |
| Git/GitHub | gitconfig copiato + ssh-agent inoltrato da VS Code | automatico |

## Uso

```bash
vibeproj nome-progetto      # crea + apre VS Code
# → Reopen in Container → claude → /prd → ./loop.sh [max-iter]
```

Superpowers: plugin globale Claude Code, già disponibile ovunque.
