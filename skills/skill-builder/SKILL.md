---
name: skill-builder
description: Crea una nuova Agent Skill per Claude Code partendo da un'idea. Guida l'utente in 5 domande (cosa fa, quando si attiva, gotcha reali, tool dipendenti, come si testa) e produce una cartella completa con SKILL.md, scripts e references seguendo le best practice Anthropic. Da invocare quando l'utente dice "creami una skill", "voglio automatizzare un workflow", "fammi una skill che fa X", o quando un prompt in CLAUDE.md sta diventando una procedura ripetuta che va estratta.
when_to_use: Richiesta esplicita di creare una skill, workflow ripetuto da automatizzare, prompt ricorrente da estrarre in formato Agent Skill, trasformazione procedura CLAUDE.md in skill dedicata
argument-hint: "[nome-skill-opzionale]"
allowed-tools: Read Write Edit Bash(ls:*) Bash(find:*) Bash(mkdir:*) Glob Grep
---

# Skill Builder

Costruisce una skill Claude Code production-ready partendo da zero, applicando le best practice ufficiali Anthropic (frontmatter validato, description in terza persona, progressive disclosure, references one-level-deep).

## When to use

Attivare quando:

- L'utente dice "creami una skill che...", "voglio una skill per...", "fammi una skill"
- Un workflow ripetuto può essere estratto in formato standalone
- Un prompt in CLAUDE.md sta diventando una procedura lunga
- L'utente vuole condividere una competenza come Agent Skill

Non attivare se:

- Il task è one-shot (non giustifica una skill)
- Non è ancora chiaro quale problema la skill risolve (chiedere prima)

## Instructions

Eseguire 5 fasi in ordine, usando AskUserQuestion tra una fase e l'altra.

### Fase 1 — Discovery (5 domande + type check)

Chiedere all'utente una per una via AskUserQuestion:

1. Cosa fa la skill? (una frase, imperativo)
2. Quando si attiva? (3 trigger phrases concrete che l'utente direbbe)
3. Qual è la gotcha più comune? (un errore che succede davvero, non ipotetico)
4. Serve accesso a tool esterni? (MCP, CLI, API, elencare)
5. Come si testa? (un comando o check verificabile)

Se l'utente non ha una gotcha reale, la skill è prematura. Suggerire di usare il workflow 2-3 volte manualmente prima di formalizzarlo in skill.

Dopo le 5 domande, classificare la skill in uno dei 4 tipi (influenza struttura e frontmatter):

| Tipo | Cosa è | Frontmatter tipico |
| --- | --- | --- |
| Task-oriented | Esegue azione concreta (commit, deploy, report) | `disable-model-invocation: true` se side effect |
| Reference | Conoscenza di dominio che Claude applica | `user-invocable: false` se background-only |
| Meta | Opera su altre skill (creator, reviewer, optimizer) | default |
| Hybrid | Task + reference combinati | default, scope esteso |

### Fase 2 — Struttura

Creare la cartella in:

- `~/.claude/skills/<name>/` se serve in più progetti (personal scope)
- `.claude/skills/<name>/` se specifica del progetto corrente (project scope)

Chiedere lo scope se non è ovvio dal contesto.

Generare la struttura standard:

```text
<skill-name>/
├── SKILL.md
├── scripts/        (solo se la skill esegue codice)
├── references/     (solo se serve documentazione on-demand)
└── assets/         (solo se produce output da template)
```

### Fase 3 — Frontmatter

Applicare le regole di validazione ufficiali (vedere [references/frontmatter-fields.md](references/frontmatter-fields.md) per il dettaglio di ogni campo):

- `name`: lowercase + trattini + numeri, max 64 char, no parole riservate (`anthropic`, `claude`)
- `description`: terza persona, max 1024 char, front-loaded; include sia il cosa sia il quando; multipli trigger per combattere under-triggering
- `when_to_use`: trigger phrases aggiuntive; combinato con description ≤ 1,536 char
- `allowed-tools`: minimal set scoped (es. `Bash(git:*)`, non `Bash` generico)
- `disable-model-invocation: true` solo per skill con side effect (deploy, commit, send)

Per esempi di description pushy vs vaghe, vedere [references/description-examples.md](references/description-examples.md).

### Fase 4 — Corpo SKILL.md

Struttura standard:

```markdown
# <Titolo>

<paragrafo intro 2-3 righe: cosa fa + valore business>

## When to use

Attivare quando:
- <trigger 1>
- <trigger 2>
- <trigger 3>

Non attivare se:
- <anti-trigger 1>
- <anti-trigger 2>

## Instructions

<step atomici, imperativi, numerati o bulleted>

## Examples

### Esempio 1: <caso tipico>
Input: <esempio concreto>
Output: <esempio concreto>

### Esempio 2: <edge case>
Input: ...
Output: ...

## Gotchas

- <errore reale + workaround>
- <errore minore + prevenzione>
- <best practice consolidata>
```

Regole d'oro:

- SKILL.md ≤ 500 righe (raccomandato dalle docs Anthropic)
- Oltre le 500 righe, spostare materiale dettagliato in `references/` e linkarlo
- Nomi file parlanti (`api_schema.json`, non `data.json`)
- Path con forward slash, mai path assoluti hardcoded
- Riferimenti a file only one level deep (no `references/a.md` che linka `references/b.md`)

### Fase 5 — Validation checklist

Prima di chiudere la skill, verificare questi 10 punti (checklist esplicita, nessuno è opzionale):

- [ ] `name` lowercase + trattini, no parole riservate (`anthropic`, `claude`)
- [ ] `description` in terza persona, front-loaded, ≥ 3 trigger concreti
- [ ] `description` + `when_to_use` combinati ≤ 1,536 char
- [ ] SKILL.md ≤ 500 righe (target < 200 per skill nuove)
- [ ] "When to use" ha sia trigger sia anti-trigger
- [ ] "Examples" con ≥ 2 casi concreti (input + output)
- [ ] "Gotchas" con errori reali, non ipotetici
- [ ] Reference file citati esistono tutti sul filesystem
- [ ] `allowed-tools` scoped (no `Bash` generico)
- [ ] Zero CAPS eccessivi nella description (CRITICAL, MUST, ALWAYS come enfasi)

### Fase 6 — Test live

Proporre all'utente di testare la skill:

```bash
# Ricaricare Claude Code per il live detection, poi invocare:
/<skill-name> <esempio input>
```

Se funziona, suggerire `/skill-reviewer <skill-name>` per audit completo (30 regole).
Se non si auto-attiva, rivedere la description (probabilmente non abbastanza specifica o in prima persona).

## Examples

### Esempio 1 — Skill `/daily-linkedin-post`

- Q1: Genera un post LinkedIn partendo dagli eventi di ieri (calendar + email)
- Q2: "Ogni mattina 9:00", "scrivi post LinkedIn", "post per LinkedIn"
- Q3: Se il giorno prima non ci sono meeting, il post viene vuoto
- Q4: OAuth Google (Gmail + Calendar), no Gmail MCP
- Q5: `/daily-linkedin-post` produce bozza > 200 parole

Risultato: `skills/daily-linkedin-post/SKILL.md` + `scripts/fetch_events.py` (OAuth).

### Esempio 2 — Skill `/audit-crm-contacts`

- Q1: Analizza contatti CRM con campi mancanti e propone fix
- Q2: "qualità CRM", "pulizia contatti", "lead inquinati"
- Q3: Se il CRM MCP non è attivo, fallisce silenziosamente
- Q4: CRM MCP (search_records, get_record_details)
- Q5: `/audit-crm-contacts` produce report con >10 candidate fix

Risultato: skill che usa AskUserQuestion per confermare soglia qualità prima del report.

## Gotchas

- Skill "tutto-fare" non si attivano: le skill focalizzate su un use case specifico si attivano meglio. Se il problema è ampio, produrre skill multiple invece di una sola.
- Gotcha ipotetica = skill prematura: se non c'è una gotcha reale, la skill non è pronta. Usare manualmente il workflow 2-3 volte prima.
- Description in prima persona: le docs Anthropic richiedono terza persona ("Genera X quando...") per auto-invocation coerente. Mai "Io genero" / "Ti aiuto a".
- `allowed-tools` senza scope: specificare sempre (es. `Bash(git:*)`, non `Bash`). Riduce l'attack surface.
- SKILL.md > 500 righe: spostare i dettagli in `references/`. Claude carica SKILL.md inline, i references on-demand.
- Claim numerici non verificabili: evitare "funziona in 3 secondi" o "2,000 template" senza fonte. Preferire claim qualitativi.
- Front-load nella description: le prime frasi sono quelle che matcha il selector. Non sprecare con intro generiche.

## References

- [references/frontmatter-fields.md](references/frontmatter-fields.md): dettaglio dei 15 campi frontmatter con esempi
- [references/description-examples.md](references/description-examples.md): 15+ esempi di description pushy vs vaghe, third-person rule, character budget

---
_Basato su [docs Anthropic skills](https://code.claude.com/docs/en/skills), [best-practices Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [skill-creator di anthropics/skills](https://github.com/anthropics/skills), pattern da [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills). MIT License._
