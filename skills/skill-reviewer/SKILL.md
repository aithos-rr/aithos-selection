---
name: skill-reviewer
description: Audita una skill Claude Code esistente contro 27 best practice Anthropic e produce un report con severity verde/giallo/rosso più fix concreti. Da attivare quando l'utente dice "rivedi questa skill", "è fatta bene?", "ottimizza la skill X", "review skill"; dopo aver usato /skill-builder per validazione pre-publish; prima di installare una skill di terze parti per screening qualità.
when_to_use: Audit skill esistente, review pre-install skill di terzi, validazione post-build, debugging skill che non si auto-attiva
argument-hint: "<path-skill-folder>"
allowed-tools: Read Glob Grep Bash(ls:*) Bash(find:*) Bash(wc:*)
---

# Skill Reviewer

Audit strutturato di una skill Claude Code contro le best practice ufficiali Anthropic. Produce un report con issue classificati per severity e fix concreti.

## When to use

Attivare quando:

- L'utente ha appena creato una skill con `/skill-builder` e vuole validarla
- Una skill non si auto-attiva più come prima
- Prima di installare una skill di terze parti (screening qualità)
- Richiesta esplicita "rivedi questa skill", "è fatta bene?", "review skill"

Non attivare se:

- La skill non esiste (proporre invece `/skill-builder`)
- Serve solo eseguire la skill (nessun audit richiesto)

## Instructions

### Fase 1 — Discovery

1. Leggere `<path>/SKILL.md`
2. `ls -la <path>/` per lista file e subfolder
3. `wc -l <path>/SKILL.md` per conta righe (target < 500)
4. Se `scripts/` esiste, listare i file e l'interprete
5. Se `references/` esiste, listare i file e la dimensione

### Fase 2 — Check frontmatter (12 regole)

Valutare ciascuna regola con verde (OK), giallo (minor), rosso (blocker).

Obbligatori:

1. `name` presente, lowercase+trattini+numeri, ≤ 64 char
2. `name` NON contiene parole riservate `anthropic` o `claude`
3. `description` presente, specifica cosa+quando, in terza persona
4. `description` + `when_to_use` combinati ≤ 1,536 char

Raccomandati:

5. `description` front-loaded (caso d'uso critico nei primi 200 char)
6. `description` contiene ≥ 3 trigger phrases concrete
7. `description` evita parole vaghe ("cose", "helper", "tool", "assistente")
8. `argument-hint` presente se la skill accetta argomenti
9. `allowed-tools` con scope (non `Bash` tout-court, usare `Bash(cmd:*)`)
10. `disable-model-invocation: true` se la skill ha side effect (deploy, commit, send)

Opzionali ma utili:

11. `paths` glob se la skill è specifica per tipo file
12. `model` o `effort` se task pesante

### Fase 3 — Check struttura cartella

13. SKILL.md < 500 righe (se supera, proporre offload in `references/`)
14. No `README.md`, `CHANGELOG.md` nella cartella skill (solo file che Claude usa)
15. Nomi file parlanti (no `data.json`, sì `api-schema.json`)
16. Script hanno shebang se eseguibili
17. Ogni file in `references/` è linkato da SKILL.md (altrimenti è orfano)
18. Path referenziati usano forward slash (no backslash Windows-style)
19. Nessun path assoluto hardcoded (`~/Dev/...`, `/Users/...`)

### Fase 4 — Check contenuto SKILL.md

20. Struttura standard: `# Titolo` → `## When to use` → `## Instructions` → `## Examples` → `## Gotchas` → `## References`
21. "When to use" ha sia trigger sia anti-trigger
22. "Instructions" con step atomici, verbi imperativi
23. "Examples" con ≥ 2 esempi concreti (input + output)
24. "Gotchas" con errori reali (non ipotetici)
25. Niente prima persona ("Io faccio") o seconda persona ("Ti aiuto")
26. Reference files linkati one-level-deep (no catene `A → B → C`)

### Fase 5 — Check audience (se pubblico business non-dev)

27. Zero jargon dev non spiegato, output orientato al risultato business

### Fase 5b — Check pattern Claude 4.5/4.6-specific

Tre regole emerse dalla community ([ActiveMemory/ctx-skill-audit](https://github.com/ActiveMemory/ctx), [okwinds/skill-review-audit](https://github.com/okwinds/miscellany)) per i modelli Claude recenti, dove i pattern di over-triggering e mandates rigidi hanno effetto peggiore che in passato.

28. Positive framing: ogni istruzione negativa ("non fare X") dovrebbe avere un counterpart positivo ("invece fai Y"). Eccezione consentita per le gotcha dichiaratamente didattiche.
29. Motivation over mandates: preferire ragionamento al posto di imperativi rigidi. Invece di "MUST NEVER...", scrivere "perché X causa problema Y, preferire Z". I modelli Claude 4.5/4.6 rispondono meglio alla motivazione che alle caps.
30. Overtriggering calibration: eccesso di CAPS emphasis nella description (CRITICAL, MUST, ALWAYS, NEVER) può causare over-triggering indesiderato. Usare caps solo per acronimi (API, JSON, YAML); preferire prose normale per enfasi.

### Fase 6 — Report

Produrre output nel formato:

```markdown
# Review `<nome-skill>`

Path: <path>

## Blocker (rosso)
- Regola N: <descrizione issue + fix concreto>

## Minor (giallo)
- Regola N: <descrizione + fix>

## OK (verde)
- Regola N

## Fix prioritari (ordine di impatto)
1. <fix più importante>
2. <fix secondo>

## Comando per applicare il primo fix
<snippet ready-to-run>
```

Criterio di publish-ready: **maggioranza verde + zero blocker rosso**. Anche con pochi minor, se i fondamentali (description, gotchas, third-person) sono OK, la skill è pubblicabile.

Dopo il report, proporre all'utente di:

1. Applicare i fix in ordine
2. Re-invocare `/skill-reviewer` per verifica post-fix
3. Se la skill passa, invitare `/skill-builder` next time per nuove skill con lo stesso standard

## Examples

### Esempio 1 — Skill ben fatta

Input: `skills/meta/skill-builder/`
Output: 26 regole verdi, 1 minor (allowed-tools potrebbe restringere ancora). Publish-ready.

### Esempio 2 — Skill problematica

Input: `skills/esperimenti/my-helper/`
Output:

- 3 blocker: description in prima persona, SKILL.md 800 righe, no trigger phrases
- 5 minor: allowed-tools `Bash` senza scope, `name` contiene "claude", path hardcoded
- Fix prioritari:
  1. Riscrivere description in terza persona con ≥ 3 trigger
  2. Rinominare skill (rimuovere parola riservata dal name)
  3. Offload materiale dettagliato in `references/full-reference.md` per scendere < 500 righe
  4. Aggiungere `## Gotchas` con ≥ 2 errori reali

## Gotchas

- Non auditare per autorità: una skill può violare una regola e avere buon motivo. Chiedere contesto prima di marcare un blocker (es. `user-invocable: false` per skill di solo background).
- Contare gli OK non basta: 25 verdi su 27 possono essere peggio di 22 su 27 se le 2 violazioni sono nei fondamentali (description, gotchas, third-person).
- Additive-only PR per skill di terzi: proporre i fix come aggiunte, non riscrittura totale. Rispettare lo stile dell'autore.
- Audit dopo ogni iterazione: ri-lanciare `/skill-reviewer` dopo ogni modifica significativa per confermare che i fix non abbiano introdotto nuovi issue.
- Le regole ufficiali possono cambiare: le docs Anthropic evolvono. Se un blocker è controverso, verificare sulla fonte pubblica prima di bloccare il publish.

## References

- [references/review-checklist.md](references/review-checklist.md): 27 regole espanse con esempi OK e KO

---
_Basato su [best-practices Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [docs Anthropic](https://code.claude.com/docs/en/skills), [agentskills.io](https://agentskills.io), pattern da [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills). MIT License._
