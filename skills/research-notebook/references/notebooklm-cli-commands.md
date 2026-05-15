# NotebookLM CLI — Cheat sheet completo

Basato su `notebooklm` v0.3.3 (installato via `uv tool install notebooklm-cli==0.3.3`).

## Contents

- [Setup (una tantum)](#setup-una-tantum)
- [Session](#session)
- [Notebooks](#notebooks)
- [Sources](#sources)
- [Chat (query grounded)](#chat-query-grounded)
- [Artefatti](#artefatti)
- [Pattern comuni](#pattern-comuni)
- [Gotchas](#gotchas)
- [Storage location](#storage-location)
- [Debug](#debug)
- [Integrazione skill](#integrazione-skill)

## Setup (una tantum)

```bash
# Install
uv tool install notebooklm-cli==0.3.3

# Login (apre browser)
notebooklm login
# Auth salvata in ~/.notebooklm/storage_state.json
```

## Session

```bash
# Lista notebook esistenti
notebooklm list

# Imposta current notebook (supporta partial ID)
notebooklm use <notebook-id>

# Mostra current session
notebooklm status

# Clear context
notebooklm clear
```

## Notebooks

```bash
# Crea
notebooklm create "Titolo del notebook"
# Output: "Created notebook: <uuid>"

# Rinomina
notebooklm rename <id> "Nuovo titolo"

# Summary AI-generated
notebooklm summary

# Elimina
notebooklm delete <id>
```

## Sources

```bash
# Aggiungi source (auto-detect tipo)
notebooklm source add "https://example.com"
notebooklm source add "https://youtube.com/watch?v=..."
notebooklm source add "./local-file.pdf"
notebooklm source add "./notes.md"
notebooklm source add "Inline text content" --title "My Notes"

# Lista sources
notebooklm source list
notebooklm source list --json  # output JSON machine-readable

# Aggiungi da Google Drive (se linked)
notebooklm source add-drive <drive-file-id>

# Aggiungi da research (ricerca web automatica)
notebooklm source add-research "query text"

# Get source details
notebooklm source get <source-id>

# Fulltext source
notebooklm source fulltext <source-id>

# Wait for source to be ready (polling)
notebooklm source wait <source-id>

# Check staleness
notebooklm source stale <source-id>

# Refresh source (re-download)
notebooklm source refresh <source-id>

# Rename source
notebooklm source rename <source-id> "New title"

# Delete source
notebooklm source delete <source-id>
```

## Chat (query grounded)

```bash
# Ask current notebook
notebooklm ask "Domanda con citazioni"

# Ask specific notebook
notebooklm ask "..." --notebook <id>

# Configure persona per chat
notebooklm configure --persona "expert" --style "concise"

# History
notebooklm history           # mostra conversazione corrente
notebooklm history save      # salva history come nota
```

## Artefatti

```bash
# Audio overview (podcast)
notebooklm generate audio

# Quiz
notebooklm generate quiz

# Mind map
notebooklm generate mind-map

# Report
notebooklm generate report
```

## Pattern comuni

### Check indicizzazione

```bash
notebooklm source list --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
srcs = d.get('sources', [])
ready = sum(1 for s in srcs if s.get('status') == 'ready')
print(f'{ready}/{len(srcs)} ready')
for s in srcs:
    if s.get('status') != 'ready':
        print(f'  [{s[\"status\"]}] {s[\"title\"][:60]}')
"
```

### Wait for indexing in bash

```bash
# Wait fino a quando tutti ready (o errore)
until [ "$(notebooklm source list --json | jq '[.sources[] | select(.status == "processing")] | length')" -eq 0 ]; do
    echo "Indexing in progress..."
    sleep 10
done
```

### Bulk add sources da lista

```bash
cat urls.txt | while read url; do
    notebooklm source add "$url"
    sleep 2  # rate limit gentle
done
```

### Query grounded con retry

```bash
# Se server busy, retry
for i in 1 2 3; do
    if response=$(notebooklm ask "$QUERY" 2>&1); then
        echo "$response"
        break
    fi
    sleep 5
done
```

## Gotchas

- 🔴 **Sources paywall**: articoli dietro paywall (Medium, NYT) falliscono con `status: error`. Usa fonte open alternativa.
- 🔴 **Limite free**: ~50 source per notebook. Oltre → crea notebook secondario.
- 🔴 **Indicizzazione timeout**: 3-5 min per source tipica. Video YouTube lunghi 10+ min.
- 🟡 **YouTube senza trascritto**: se video non ha captions/CC, NotebookLM può avere info limitate.
- 🟡 **PDF scansionati**: se sono immagini (no OCR), NotebookLM non li legge.
- 🟡 **Citations attribution**: le citazioni `[1][2]` possono a volte puntare a source sbagliata. Verifica manualmente per fatti critici.
- 🟢 **Notebook per tema focalizzato**: meglio 10 notebook temati di 1 generico.
- 🟢 **Re-ask per chiarire**: se risposta vaga, chiedi "quali fonti specifiche? quale citazione?" — il follow-up affina.

## Storage location

```
~/.notebooklm/
├── storage_state.json    # Google auth (NON commitare in git!)
└── cache/                # cache file downloaded
```

## Debug

```bash
# Verbose
notebooklm -vv ask "..."

# Check version
notebooklm --version

# Override storage location
notebooklm --storage /path/to/custom/state.json list
```

## Integrazione skill

Questa skill `/research-notebook` automatizza:
1. `create` + `use` new notebook
2. `source add` in batch
3. Wait for indexing
4. `ask` con query progressive
5. Save output in Obsidian via skill `/obsidian-brain`
