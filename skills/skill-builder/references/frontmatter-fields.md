# Frontmatter SKILL.md — Catalogo 15 campi

Sintesi dalle [docs ufficiali Anthropic](https://code.claude.com/docs/en/skills) e [best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Contents

- [Obbligatori (de facto)](#obbligatori-de-facto)
- [Raccomandati](#raccomandati)
- [Controllo invocazione](#controllo-invocazione)
- [Permessi tool](#permessi-tool)
- [Execution](#execution)
- [Lifecycle](#lifecycle)
- [String substitutions supportate nel body](#string-substitutions-supportate-nel-body)
- [Dynamic context injection](#dynamic-context-injection)
- [Esempio completo](#esempio-completo)
- [Quando un campo è opzionale vs utile](#quando-un-campo-%C3%A8-opzionale-vs-utile)

## Obbligatori (de facto)

### `name`
- **Tipo**: string
- **Formato**: `lowercase-with-hyphens`, max 64 char
- **Default se omesso**: nome della cartella
- **Esempio**: `name: morning-briefing`

### `description`
- **Tipo**: string (max 1,536 char combinato con `when_to_use`)
- **Obiettivo**: innesca auto-invocation. Scrivi cosa fa + quando si attiva.
- **Esempio**: `description: "Triage inbox Gmail + genera bozze. Da usare con backlog >20 email o dopo ferie."`
- **Anti-pattern**: "Helper per email" (vago, no trigger)

## Raccomandati

### `when_to_use`
- **Tipo**: string
- **Obiettivo**: trigger aggiuntivi — parole chiave user, tipi file, situazioni
- **Esempio**: `when_to_use: "Backlog email >20, rientro ferie, inbox accumulata"`

### `argument-hint`
- **Tipo**: string
- **Obiettivo**: hint autocompletamento per slash command
- **Esempio**: `argument-hint: "[issue-number]"`

### `arguments`
- **Tipo**: space-separated string o YAML list
- **Obiettivo**: named positional args per `$name` substitution
- **Esempio**: `arguments: [component, source, target]` → usa `$component` nel body

## Controllo invocazione

### `disable-model-invocation`
- **Tipo**: boolean (default false)
- **Usa quando**: skill ha side effect (deploy, commit, send email)
- **Effetto**: solo user può invocare via `/name`, Claude non auto-attiva

### `user-invocable`
- **Tipo**: boolean (default true)
- **Usa quando**: skill è solo background knowledge (es. `legacy-system-context`)
- **Effetto**: non appare in `/` menu

## Permessi tool

### `allowed-tools`
- **Tipo**: space-separated string o YAML list
- **Obiettivo**: pre-approva tool senza prompt per l'utente
- **Esempio**: `allowed-tools: Read Grep Bash(git *)`
- **Anti-pattern**: `allowed-tools: Bash` (troppo permissivo, restringi con `Bash(comando *)`)

## Execution

### `model`
- **Tipo**: model ID stringa o `inherit`
- **Esempio**: `model: claude-sonnet-4-6`
- **Effetto**: override session model per la durata skill

### `effort`
- **Tipo**: `low`, `medium`, `high`, `xhigh`, `max` (dipende dal modello)
- **Default**: inherit session
- **Esempio**: `effort: high` per task complessi

### `context`
- **Tipo**: `fork` (o omesso)
- **Effetto**: esegue in subagent isolato (no history sessione)
- **Uso tipico**: research skill con `agent: Explore`

### `agent`
- **Tipo**: string (es. `Explore`, `Plan`, `general-purpose`, custom subagent)
- **Richiesto se**: `context: fork` attivo
- **Esempio**: `agent: Explore` per skill di ricerca codebase

## Lifecycle

### `hooks`
- **Tipo**: mapping (spec completa in `hooks` docs)
- **Obiettivo**: azioni scoped al lifecycle skill
- **Esempio**: hook on skill invocation/completion

### `paths`
- **Tipo**: glob comma-separated o YAML list
- **Effetto**: attiva skill auto solo quando si lavora su file matching
- **Esempio**: `paths: "src/**/*.tsx, src/**/*.ts"`

### `shell`
- **Tipo**: `bash` (default) o `powershell`
- **Uso**: specifica shell per `!`comandi`` inline
- **Requisito PowerShell**: `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` env var

## String substitutions supportate nel body

- `$ARGUMENTS` — tutti gli argomenti passati
- `$ARGUMENTS[N]` o `$N` — argomento specifico per posizione 0-based
- `$nome` — named argument (vedi `arguments` sopra)
- `${CLAUDE_SESSION_ID}` — session ID corrente
- `${CLAUDE_SKILL_DIR}` — directory della skill (per referenziare file bundled)

## Dynamic context injection

Puoi eseguire comandi shell nel body SKILL.md che vengono sostituiti con l'output PRIMA che Claude legga:

```markdown
## Context

- PR diff: !`gh pr diff`
- Current git status: !`git status --short`
```

Multi-line:
````markdown
## Environment
```!
node --version
git status --short
```
````

Claude riceve il risultato sostituito, non il comando.

## Esempio completo

```yaml
---
name: pr-summary
description: Summarize pull request changes with context
when_to_use: Review PR, summarize changes, code review intro
argument-hint: "[pr-number]"
context: fork
agent: Explore
allowed-tools: Bash(gh *) Read Grep
effort: medium
---

# PR Summary

## Context
- PR diff: !`gh pr diff $0`
- PR comments: !`gh pr view $0 --comments`

## Your task

Summarize this PR focusing on:
1. High-level intent (why was this change made?)
2. Risk areas (what could break?)
3. Review hotspots (what deserves extra attention?)

Keep summary under 300 words.
```

## Quando un campo è opzionale vs utile

Regola: **se non cambia comportamento rispetto al default, non scriverlo**. Frontmatter pulito > frontmatter completo.

Esempio:
```yaml
# OK — minimo necessario
---
name: my-skill
description: Cosa fa e quando usarla
---
```

vs

```yaml
# Troppo verboso — i default bastano
---
name: my-skill
description: ...
disable-model-invocation: false    # default
user-invocable: true                # default
shell: bash                         # default
---
```
