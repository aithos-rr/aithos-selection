---
name: ultra-think-plan
description: Orchestratore per task ad alto calibro che combina la keyword ultrathink (thinking budget esteso) con /ultraplan (plan mode in cloud). Da attivare quando il task è complesso (architettura, debugging profondo, trade-off analysis, refactor multi-file, decisioni strategiche), quando l'utente dice "pensa bene a X", "serve un piano per Y", "problema complesso Z", o quando la soluzione richiede esplorazione di 3+ alternative. Include una checklist costo/beneficio per decidere se attivare l'orchestratore o rispondere diretto.
when_to_use: Task complessi, architettura, debugging difficile, decisioni strategiche, grandi refactor, analisi di sistemi interconnessi
argument-hint: "<descrizione-problema>"
model: inherit
effort: high
allowed-tools: Read Grep Glob
---

# Ultra Think + Plan

Orchestratore che decide quando e come usare i due poteri di thinking avanzato in Claude Code:

1. `ultrathink` — keyword che attiva un thinking budget esteso (vedere [references/ultrathink-keyword.md](references/ultrathink-keyword.md) per i dettagli).
2. `/ultraplan` — comando che sposta il planning in cloud sandbox Anthropic (vedere [references/ultraplan-workflow.md](references/ultraplan-workflow.md)).

Usati insieme, trasformano un task complesso da "ore di tentativi" a "pensiero profondo + esecuzione guidata".

## When to use

Attivare quando:

- Il task tocca molti file o sistemi interconnessi
- Servono trade-off analysis (stack choice, architettura)
- Debugging difficile (bug intermittente, issue multi-layer)
- Grande refactor con molte dipendenze
- L'utente dice "pensa a fondo", "voglio un piano solido", "problema complesso"

Non attivare se:

- Task banale o ben definito (spreco di budget)
- Fix tipografico o 1-2 file (rispondere direttamente)
- Bug con stacktrace chiaro (andare diretto al fix)

## Checklist costo/beneficio

Prima di invocare ultrathink / ultraplan, valutare:

| Dimensione | Basso costo (skip ultra) | Alto costo (usa ultra) |
| --- | --- | --- |
| File toccati | 1-3 | 5+ |
| Soluzioni possibili | 1 ovvia | 3+ alternative |
| Rischio regressione | Basso | Alto (produzione, dati, revenue) |
| Tempo tentativo manuale | < 30 min | > 2 ore |
| Reversibilità | Facile revert | Difficile o costoso |

Se ≥ 2 righe sono "alto costo" → invocare l'orchestratore. Altrimenti rispondere diretto.

## Instructions

### Fase 1 — Comprensione del problema

1. Leggere `<descrizione-problema>` dall'utente
2. Esplorare il contesto con Read, Grep, Glob (max 10 file rilevanti)
3. Attivare ultrathink inserendo la keyword `ultrathink` nel ragionamento interno
4. Ragionare su:
   - Quali sono le 3 interpretazioni possibili del problema?
   - Quali informazioni mancano?
   - Quali vincoli impliciti esistono?
   - Quali sono 3 approcci radicalmente diversi?

### Fase 2 — Decisione: local vs cloud plan

Chiedere all'utente via AskUserQuestion:

- Local plan mode (plan mode standard di Claude Code): se l'utente vuole iterare insieme
- `/ultraplan` cloud: se il problema è ben definito, serve un plan robusto in background, o serve review inline con commenti

### Fase 3A — Local plan

1. Entrare in Claude Code plan mode (`Shift+Tab` o `/plan`)
2. Generare il plan con 3 alternative, pro/contro per ognuna
3. Includere una sezione "Verification"
4. Proporre le alternative via AskUserQuestion
5. Uscire dal plan mode e procedere con l'esecuzione

### Fase 3B — Cloud plan

Vedere [references/ultraplan-workflow.md](references/ultraplan-workflow.md) per il workflow completo.

Sintesi:

1. Spiegare all'utente che `/ultraplan <descrizione>` apre una sandbox cloud con plan generato
2. Generare il comando completo con la descrizione del problema
3. L'utente lancia `/ultraplan` e riceve l'URL della sandbox
4. Plan review inline
5. All'approvazione, scegliere tra esecuzione remota (con PR automatica) o download del plan per esecuzione locale

### Fase 4 — Verifica del plan (prima di eseguire)

Applicare le 5 domande al plan generato:

1. Goal-backward: il plan produce davvero l'outcome desiderato?
2. Edge cases: il plan copre i 3 edge case più rischiosi?
3. Verification: come sappiamo che ha funzionato (criterio oggettivo, non "speriamo")?
4. Rollback: se qualcosa va male, come si torna indietro?
5. Time: stima realistica o ottimistica?

Se ≥ 2 risposte sono insoddisfacenti → rigenerare il plan con i fix prima di eseguire.

## Examples

### Esempio 1 — Refactor schema database in produzione

Problema: "Spostare 3 tabelle da Postgres a MongoDB, 50M record, zero downtime".

Checklist: file toccati 15+, alternative 4+, rischio altissimo (production + dati), tempo manuale > 1 giorno, reversibilità quasi impossibile.

→ Invocare ultra-think-plan. Fase 1 ultrathink, Fase 3B cloud plan (sandbox per testare la migration su dataset sintetico), Fase 4 goal-backward verify.

### Esempio 2 — Bug intermittente in produzione

Problema: "~1 request su 1000 ritorna 500, non si riproduce in staging".

Checklist: file toccati sconosciuto, alternative 5+ ipotesi, rischio medio-alto, già 4 ore perse.

→ Invocare ultra-think-plan. Fase 1 ultrathink (analisi log + correlazione), Fase 3A local plan (debugging iterativo), Fase 4 verify con repro minimale.

### Esempio 3 — Skip

Problema: "Errore 'Cannot read property of undefined' in Login.jsx linea 42".

Checklist: tutto basso costo.

→ Skip ultra-think-plan. Leggere linea 42 e applicare fix diretto.

## Gotchas

- ultrathink non funziona in Claude.ai web interface: solo Claude Code CLI e le sue varianti (desktop, IDE extension, cloud) supportano la keyword. In chat normale viene ignorata.
- `/ultraplan` richiede piano Anthropic attivo con credit disponibile: il cloud plan mode consuma dal piano Anthropic, non dal Claude Code locale.
- Abuso della keyword: usare ultrathink su ogni prompt aumenta il budget ma non la produttività. Rispettare la checklist costo/beneficio.
- Cloud plan ≠ ambiente locale: la sandbox può non avere accesso a file locali sensibili (.env, credenziali). Verificare i path prima di lanciare.
- Plan robusto ≠ esecuzione robusta: un plan perfetto non garantisce esecuzione perfetta. Applicare sempre la fase 4 di verification.
- Scope discipline: questa skill pianifica, non esegue. Dopo il plan approvato, l'esecuzione avviene nel flow standard di Claude Code (o remote via `/ultraplan` se cloud). Non estendere la skill a eseguire direttamente.

## References

- [references/ultrathink-keyword.md](references/ultrathink-keyword.md): come funziona il thinking budget esteso e quando attivarlo
- [references/ultraplan-workflow.md](references/ultraplan-workflow.md): flow completo del cloud plan mode

---
_Basato su [claudelog — ultrathink](https://claudelog.com/faqs/what-is-ultrathink/), [stevekinney — Claude ultraplan](https://stevekinney.com/writing/claude-ultraplan), [docs Anthropic skills](https://code.claude.com/docs/en/skills). MIT License._
