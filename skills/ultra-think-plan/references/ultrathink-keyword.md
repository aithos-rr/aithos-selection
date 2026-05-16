# ultrathink — keyword Claude Code

## Contents

- [Cosa fa](#cosa-fa)
- [Quando funziona (e quando no)](#quando-funziona-e-quando-no)
- [Varianti e livelli](#varianti-e-livelli)
- [Quando attivarlo](#quando-attivarlo)
- [Costo](#costo)
- [Pattern di uso](#pattern-di-uso)
- [Anti-pattern](#anti-pattern)
- [Verifica](#verifica)
- [Combinazione con /ultraplan](#combinazione-con-ultraplan)
- [Fonte](#fonte)

## Cosa fa

Inserire la parola `ultrathink` in qualsiasi prompt in Claude Code CLI attiva il massimo thinking budget disponibile: **31,999 token** (vs ~8-16k default).

Claude usa questi token per ragionare in profondità PRIMA di rispondere: esplora alternative, argomenta con sé stesso, backtracca, riconsidera, sintetizza.

## Quando funziona (e quando no)

### ✅ Funziona in:
- Claude Code CLI (terminale)
- Claude Code extension (VS Code, JetBrains)
- Claude Code on the web (claude.ai/code)
- Claude Agent SDK

### ❌ NON funziona in:
- Claude.ai web interface (chat normale)
- Claude API direct call (senza Code framework)
- Altri tool che usano Anthropic API

Se scrivi `ultrathink` in chat.claude.com, non succede niente. È una keyword specifica Claude Code.

## Varianti e livelli

Alcuni keyword correlati (da test community, non tutti documentati):

| Keyword | Token budget approx |
|---------|---------------------|
| default | 8,000-16,000 |
| `think hard` | ~20,000 |
| `think harder` | ~25,000 |
| `ultrathink` | 31,999 |

**Nota**: i livelli intermedi possono variare per versione Claude Code. `ultrathink` è il più stabile.

## Quando attivarlo

### Usa ultrathink

- **Architettura**: "progetta il sistema X che supporta Y utenti con vincoli Z"
- **Debug difficile**: bug intermittente, issue multi-layer, race condition
- **Trade-off analysis**: "stack A vs B vs C con questi constraint"
- **Refactor grosso**: impatto su 10+ file, dipendenze complesse
- **Decisione strategica**: "dovremmo andare con approach X?"

### Evita ultrathink

- Task ovvio (fix tipo, typo, rename)
- Quando la risposta è una ricerca di 1 file
- Per domande di conoscenza generale (Claude sa già, non deve pensarci)

## Costo

Più thinking = più token consumati = più costo.

Ordine di grandezza:
- Chiamata standard: ~$0.01 - $0.05
- Con ultrathink: ~$0.10 - $0.40 per task complesso

Se fai 20 ultrathink al giorno, è ~$4-8/giorno. Vale la pena SOLO se ti fa risparmiare tempo significativo su task rilevanti.

## Pattern di uso

### Pattern 1: Ultrathink + Plan mode

Per decisioni architetturali:
```
/plan <problema complesso>
<dentro plan mode>
ultrathink this approach carefully: [proposta]
```

Claude analizza profondamente la proposta prima di confermarla.

### Pattern 2: Ultrathink + multiple alternatives

Per trade-off:
```
ultrathink: dammi 3 approcci diversi per [problema], con pros/cons per ognuno
considerando [vincoli specifici]
```

### Pattern 3: Ultrathink on error

Per debug complesso:
```
ultrathink this bug: [stacktrace]
Considera tutti i possibili root cause, anche quelli non ovvi.
Pensa a race condition, edge case, stato condiviso, cache.
```

## Anti-pattern

- 🔴 **Ultrathink in ogni prompt**: abuso, costo alto senza beneficio
- 🔴 **Ultrathink su task ovvio**: tipo fix, Claude perde tempo
- 🔴 **Aspettarsi che funzioni in web UI**: non funziona, keyword Claude Code only

## Verifica

Non c'è modo diretto di verificare "quanti token di thinking ha usato Claude". Ma puoi:
- Osservare la risposta: se usa ultrathink, tipicamente produce più alternative, più qualificazione, più edge case considerati
- Misurare il costo in Anthropic dashboard (spike quando usi ultrathink)

## Combinazione con /ultraplan

`/ultraplan` (cloud plan mode) e `ultrathink` (extended thinking) sono complementari:

- **ultrathink**: profondità su UN prompt/risposta
- **/ultraplan**: planning mode in cloud sandbox, multi-step

Vedi `ultraplan-workflow.md` per dettagli.

## Fonte

- [claudelog.com/faqs/what-is-ultrathink/](https://claudelog.com/faqs/what-is-ultrathink/)
- Discussioni community: Hacker News #43739997
