---
name: agent-memory-starter
description: Wizard che genera un file CLAUDE.md personalizzato via 10 domande guidate (ruolo, tono, stack, routine). Produce un CLAUDE.md compilato in 5 minuti, pronto da committare. Attiva al primo setup di Claude Code, per nuovi progetti, o per rifare da zero un CLAUDE.md bloated. Applica progressive disclosure per evitare file oltre 200 righe.
when_to_use: Primo setup Claude Code, nuovo progetto, rifacimento CLAUDE.md, template starter, onboarding
argument-hint: "[global|project]"
allowed-tools: Read Write Edit
---

# Agent Memory Starter

Wizard interattivo da 10 domande che produce un CLAUDE.md production-ready. Pensato per utenti non-dev che aprono Claude Code per la prima volta e non sanno cosa mettere nel file di memoria.

## When to use

Attiva quando:

- Primo setup di Claude Code (CLAUDE.md non esiste)
- Nuovo progetto in cui serve un CLAUDE.md project-level
- CLAUDE.md esistente vecchio, bloated o confuso
- L'utente dice "setup Claude", "configura Claude", "come iniziare"

Non attivare se:

- CLAUDE.md esiste ed è buono (proponi invece una review con `/skill-reviewer` se applicabile)
- Richiesta specifica di modificare una sezione (proponi un edit mirato)

## Scope

Argomento `[global|project]`:

- `global`: crea `~/.claude/CLAUDE.md` (regole personali universali)
- `project`: crea `<cwd>/CLAUDE.md` (contesto progetto specifico)

Se omesso, chiedere via AskUserQuestion.

## Instructions

### Fase 1 — 10 domande (AskUserQuestion, una per volta)

Block 1 — Chi sei (se global):

1. Nome e ruolo: "Sono [nome], [ruolo] presso [azienda]"
2. Background: developer / non-developer / figura ibrida (GTM, data, PM, designer)
3. Progetti attivi: 2-4 progetti principali

Block 2 — Come lavori:

4. Tono preferito: formale / diretto / casual / tecnico
5. Modalità default: execute (veloce) / review (metodico) / learn (didattico)

Block 3 — Stack:

6. Tool principali per area (CRM, email, workflow, research). Esempio: "CRM: HubSpot; email: Mailchimp; workflow: n8n"
7. Lingua: italiano per comunicazione, inglese per codice, o mix

Block 4 — Preferenze (se project, sono facoltativi):

8. Engineering preferences: DRY, attitudine ai test, tolleranza over-engineering
9. Privacy: livello dati sensibili, tool da non usare mai
10. Quando le cose vanno male: cosa fare (chiedere subito / tentare alternativa / log e prosegui)

### Fase 2 — Genera CLAUDE.md

Vedere [references/claude-md-examples.md](references/claude-md-examples.md) per 3 template compilati (marketer, founder, PM). Vedere [references/sections-library.md](references/sections-library.md) per la libreria di 15 sezioni opzionali.

Template base:

```markdown
# Chi sono

[Risposte 1-2: ruolo, azienda, background]

**Lingua**: [Risposta 7]

## Progetti attivi

[Risposta 3 come lista]

## Modalità operative

### Execute mode (default)
[Tono basato su risposte 4-5]

### Review mode (attiva con `/review`)
Analisi strutturata. Per ogni issue: problema → opzioni → raccomandazione → conferma.

### Learn mode
Spiega il cosa e il perché. Commenta, usa analogie.

## Engineering Preferences

[Risposta 8 come bullet]

## Stack operativo

[Risposta 6 espansa come "Tool X → <uso>"]

## Quando le cose vanno male

[Risposta 10 + fallback standard]

## Privacy e dati sensibili

[Risposta 9]

## Persona

[Risposta 4 come tono comunicazione]
```

### Fase 3 — Review con l'utente

Mostrare il file generato e proporre sezioni opzionali:

> "Vuoi aggiungere una delle seguenti sezioni? (vedi references/sections-library.md)
> - Obsidian workflow (secondo cervello)
> - NotebookLM research stack
> - Skill pack installato
> - Routing MCP server"

Se l'utente conferma, appendere la sezione dalla libreria.

### Fase 4 — Salva

```bash
# Se global
cp generated.md ~/.claude/CLAUDE.md

# Se project
cp generated.md ./CLAUDE.md
```

Se il file esiste già, chiedere: overwrite / append / skip / mostra diff.

### Fase 5 — Prossimi passi

Messaggio finale:

```text
CLAUDE.md creato in <path>

Prossimi step:
1. Testa: chiedi a Claude "chi sono?" — deve rispondere dal file
2. Committa CLAUDE.md in git per tracciare l'evoluzione
3. Ri-lancia /agent-memory-starter quando cambi ruolo, stack o progetti
```

## Examples

Esempio 1 — Marketer freelance:

Risposte sintetiche: Luca Rossi, freelance marketing, non-dev, 3 clienti SaaS B2B, tono diretto, execute default, stack Airtable+Mailchimp+n8n, italiano per comm e inglese per codice, minimum viable, GDPR sempre, conferma prima di azioni su account cliente.

Output: CLAUDE.md di circa 120 righe.

Esempio 2 — Founder early-stage:

Risposte minimali (velocità prima di tutto).

Output: CLAUDE.md di circa 80 righe, essenziale.

## Gotchas

- Nessun campo vuoto: se l'utente salta una domanda, proporre un default sensato; non lasciare placeholder `<TODO>` nel file finale.
- Un solo CLAUDE.md per scope: se esiste già un file al path target, mostrare il diff e chiedere conferma prima di sovrascrivere.
- Progressive disclosure: un CLAUDE.md oltre 200 righe è sintomo di bloat. Se l'utente vuole più contenuto, proporre di spostare i dettagli in file linkati o in skill dedicate.
- Versioning: commitare CLAUDE.md in git per vedere l'evoluzione del ruolo nel tempo.
- Refresh periodico: ogni 6 mesi il contesto di ruolo, stack e progetti cambia. Ri-lanciare questa skill come routine di manutenzione.
- Scope discipline: questa skill genera un CLAUDE.md da zero via wizard. Per modificare una singola sezione di un CLAUDE.md esistente e funzionante, proporre invece un edit mirato con il tool Edit. La skill entra in gioco quando serve un refactor completo o un setup iniziale.

## References

- [references/claude-md-examples.md](references/claude-md-examples.md): 3 esempi compilati per profili tipo (marketer, founder, PM)
- [references/sections-library.md](references/sections-library.md): libreria di 15 sezioni opzionali con criteri di inclusione

---
_Basato su [docs Anthropic](https://code.claude.com/docs/en/skills), [agentskills.io](https://agentskills.io). MIT License._
