# Description Examples — 15+ pattern pushy vs vaghi

Raccolta di description reali commentate, applicando le regole ufficiali Anthropic ([best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## Contents

- [Regole hard da rispettare](#regole-hard-da-rispettare)
- [Pattern "Instead of X, write Y"](#pattern-instead-of-x-write-y)
- [15 esempi annotati](#15-esempi-annotati)
- [Third-person rule](#third-person-rule)
- [Character budget combinato](#character-budget-combinato)
- [Trigger phrases pushy](#trigger-phrases-pushy)

## Regole hard da rispettare

Dalle docs ufficiali Anthropic:

- `description` ≤ 1024 char, non vuota, no XML
- Combined `description` + `when_to_use` ≤ 1,536 char (truncation budget)
- Terza persona sempre ("Genera X" / "Processes Y"), mai "Ti aiuto" o "Puoi usare"
- Front-load del caso d'uso critico nelle prime 100 parole
- Include sia il cosa sia il quando

## Pattern "Instead of X, write Y"

Esempio ufficiale dalle docs Anthropic:

> Instead of: "How to build a simple fast dashboard to display internal data."
>
> Write: "How to build a simple fast dashboard to display internal data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard'."

La versione pushy esplicita i trigger + i sinonimi che l'utente potrebbe usare.

## 15 esempi annotati

### 1. PDF processing (esempio ufficiale Anthropic)

**Bene**: `Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.`

Perché: terza persona, verbi multipli (extract/fill/merge), trigger espliciti (PDF, forms, extraction).

### 2. Excel analysis (esempio ufficiale Anthropic)

**Bene**: `Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.`

Perché: lista di estensioni file (.xlsx) + sinonimi (spreadsheets / tabular data).

### 3. Git commit helper (esempio ufficiale Anthropic)

**Bene**: `Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.`

### 4. Lead enrichment (case Learnn-like)

**Bene**: `Arricchisce una lista di lead con azienda, ruolo, email verificata e segnali intent. Da usare quando l'utente ha un CSV o Google Sheet di contatti grezzi, serve rifinire una lista prima di outreach, quando si parla di "lead dirty" o "lead qualification".`

**Male**: `Aiuta con i lead` — vago, non specifica cosa fa né quando.

### 5. Morning briefing

**Bene**: `Produce un briefing mattutino con email non lette prioritarie, eventi Calendar di oggi, file Drive modificati nelle ultime 24h. Attivare ogni mattina alle 8:00 oppure quando l'utente dice "come inizia la mia giornata", "cosa c'è oggi", "briefing".`

**Male**: `Ti mostra cosa hai da fare oggi` — seconda persona, niente trigger.

### 6. Research notebook

**Bene**: `Orchestra NotebookLM per una ricerca grounded zero-hallucination con citazioni verificabili. Crea il notebook, aggiunge fonti (URL, PDF, YouTube), attende l'indicizzazione, formula query grounded. Attivare quando serve ricerca con citazioni, trascritti YouTube, volumi > 50 fonti, docs tecniche nuove.`

### 7. Vague (da correggere)

**Male**: `Helper per documenti` → **Bene**: `Gestisce file .docx: crea nuovi documenti, modifica testo esistente, applica tracked changes. Usare quando si lavora con file Word, OOXML, o documenti editati da più persone.`

### 8. Prima persona (da correggere)

**Male**: `Posso aiutarti a creare presentazioni` → **Bene**: `Crea presentazioni strutturate da un outline markdown. Genera slide title, body, note speaker in formato compatibile con Canva/Keynote/Google Slides.`

### 9. Seconda persona (da correggere)

**Male**: `Ti genera il report settimanale` → **Bene**: `Genera un report settimanale analizzando la cartella Drive dedicata, estraendo metriche ricorrenti e producendo un breve report narrativo + foglio Excel. Attivare ogni venerdì alle 17:00 oppure quando l'utente dice "report della settimana" o "come è andata".`

### 10. Trigger insufficienti

**Male**: `Crea skill` → **Bene**: `Wizard che crea una nuova skill Claude Code guidando in 5 domande. Attivare quando l'utente dice "creami una skill", "voglio automatizzare questo workflow", "fammi una skill che fa X", o quando un prompt in CLAUDE.md sta diventando una procedura ripetuta.`

### 11. Troppo lunga (oltre 1024 char)

**Male**: 2000 caratteri con 30 trigger e 5 paragrafi di esplicazione → **Bene**: tagliare a 500-800 char, spostare esempi in body SKILL.md.

### 12. Domain-specific business audience

**Bene**: `Costruisce un workflow n8n partendo da una descrizione in linguaggio naturale. Traduce concetti business (lead, campagna, CRM) in nodi n8n (Code, HTTP, Webhook). Attivare quando l'utente descrive un processo che "si dovrebbe automatizzare" o menziona n8n, workflow, automazione business.`

### 13. Skill reference (load-on-demand)

**Bene**: `API conventions per il codebase MyProject. Applica quando si scrivono endpoint, si modificano controller, si rivedono PR che toccano la route layer.` + `user-invocable: false` nel frontmatter (è conoscenza di background, non un'azione).

### 14. Skill task con side effect

**Bene**: `Stage and commit current changes with a descriptive message generated from the diff. Use when the user asks to commit, save changes, or finalize work.` + `disable-model-invocation: true` (l'utente deve decidere il timing del commit).

### 15. Multi-trigger con sinonimi

**Bene**: `Audita una skill esistente contro 27 best practice Anthropic, produce report con severity verde/giallo/rosso. Attivare quando l'utente dice "rivedi questa skill", "controlla la mia skill", "è ok questa skill?", "review skill", o dopo aver usato /skill-builder per la prima validazione.`

## Third-person rule

Regola ufficiale: *"Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems."*

| Vietato (I / You) | Corretto (terza persona) |
|-------------------|--------------------------|
| I can help you process PDFs | Processes PDFs, extracts text, fills forms |
| Ti aiuto a creare skill | Crea skill Claude Code guidando in 5 domande |
| You can use this to... | [verbo attivo]... |
| Posso generare report | Genera report settimanali da cartella Drive |

In italiano, la "terza persona impersonale" corretta usa verbi in modo indicativo attivo ("Genera", "Analizza", "Audita") oppure infinito narrativo ("Costruire", "Orchestrare").

## Character budget combinato

Formula: `description + when_to_use ≤ 1,536 char`.

Esempio corretto (combinato 800 char):

```yaml
description: Genera report settimanale analizzando Drive, Gmail, Calendar. Produce Excel + narrativa. Attivare ogni venerdì 17:00 o su richiesta esplicita ("report settimanale", "come è andata la settimana").
when_to_use: Venerdì pomeriggio, richiesta review settimanale, chiusura sprint, retrospettiva team
```

Se la somma supera 1,536, il testo viene troncato nel registry di skill e Claude potrebbe non matchare i trigger finali.

## Trigger phrases pushy

Lista di formule efficaci per il bloco "Use when" della description:

- `Use when working with <file type>` — matcha su tipo di file
- `Use when the user mentions <synonym1>, <synonym2>, or <synonym3>` — matcha su sinonimi
- `Activate ogni [frequenza]` — matcha su routine temporali
- `Attivare quando l'utente dice "X", "Y", "Z"` — matcha su frasi dirette
- `Use after <previous action>` — matcha su sequenze di lavoro
- `Even if the user doesn't explicitly ask for X` — esplicita che la skill copre anche casi indiretti

---
_Fonti: [best-practices Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [docs Anthropic](https://code.claude.com/docs/en/skills), [agentskills.io](https://agentskills.io)._
