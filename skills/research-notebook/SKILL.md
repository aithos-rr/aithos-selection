---
name: research-notebook
description: Orchestra NotebookLM (Google) per ricerca grounded con citazioni verificabili. Crea o riusa un notebook, aggiunge sorgenti (URL web, video YouTube, PDF, file locali), attende l'indicizzazione, pone query progressive e salva la sintesi finale in un vault Obsidian con frontmatter completo. Da attivare per research approfondita, analisi video YouTube (anti-allucinazione trascritti), documentazioni tecniche nuove, volumi di fonti oltre le 10, ogni volta che servono citazioni verificabili. L'utente dice "ricerca su X", "voglio capire a fondo Y", "analizza questi materiali".
when_to_use: Research approfondita con citazioni, video YouTube, documentazione tecnica nuova, volumi > 10 fonti, paper accademici, sintesi multi-sorgente
argument-hint: "<tema-ricerca>"
allowed-tools: Bash(notebooklm:*) Write Read
---

# Research Notebook

Orchestra NotebookLM per ricerca zero-hallucination con citazioni verificabili. Claude orchestra (crea notebook, aggiunge sorgenti, pone query, salva sintesi); NotebookLM elabora grounded sui server Google; Obsidian archivia la sintesi finale. Basato sulla CLI pubblica `notebooklm-cli` (vedere [references/notebooklm-cli-commands.md](references/notebooklm-cli-commands.md)).

## When to use

Attivare quando:

- È necessario analizzare video YouTube (senza trascritti reali il modello allucina)
- Documentazione tecnica nuova (anti-allucinazione su API non viste in training)
- Volumi grandi di fonti (> 10) da sintetizzare con citazioni
- Richiesta esplicita di risposta con citazioni verificabili `[1][2][3]`

Non attivare se:

- Query web semplice (bastano i tool standard di web search)
- L'informazione è già nel vault Obsidian (cercare prima)
- Domanda su codebase locale (usare Grep e Read diretti)

## Prerequisiti

Il partecipante deve avere `notebooklm-cli` installato:

```bash
uv tool install notebooklm-cli==0.3.3
notebooklm login   # apre browser e richiede login Google
```

Se la CLI non è installata, la skill stampa le istruzioni di setup e termina.

Il path del vault Obsidian deve essere noto. Il wizard al primo uso lo chiede una volta e lo salva come variabile nel session context (o in un file di config a scelta dell'utente). Default suggerito: `~/Documents/Obsidian/<vault>/02-Ricerca/`.

## Instructions

### Fase 1 — Chiarificare il tema

Chiedere all'utente via AskUserQuestion:

1. Tema della ricerca in una frase (es. "migliori pratiche GTM per SaaS B2B")
2. Sorgenti: URL web, YouTube, PDF online, file locali (PDF, markdown)
3. Vault path di destinazione per la sintesi (se non già configurato)

### Fase 2 — Creare o riusare il notebook

```bash
# Verificare esistenza
notebooklm list | grep -i "<tema-keyword>"

# Se non esiste, creare
notebooklm create "<titolo-descrittivo>"
# Output: "Created notebook: <notebook_id>"

# Impostare come attivo
notebooklm use <notebook_id>
```

### Fase 3 — Aggiungere sorgenti

Per ogni sorgente:

```bash
# URL web, YouTube, PDF online
notebooklm source add "<url>"

# File locale
notebooklm source add "/path/to/file.pdf"
notebooklm source add "/path/to/note.md"
```

Aggiungere sorgenti a batch da 10-20. NotebookLM free ha un limite di circa 50 sorgenti per notebook (valore soggetto a cambiamento, verificare nella UI).

### Fase 4 — Attendere l'indicizzazione

```bash
notebooklm source list --json | python3 -c "import json,sys; d=json.load(sys.stdin); srcs=d.get('sources',[]); print(sum(1 for s in srcs if s.get('status')=='ready'),'/',len(srcs),'ready')"
```

Attendere finché tutte le sorgenti risultano `ready` (tempo tipico ~3 minuti). Le sorgenti in errore (paywall, link morti) vanno ignorate.

### Fase 5 — Query grounded progressive

Porre 3-7 query in questa sequenza:

1. Panoramica: "Dammi un overview del tema con citazioni"
2. Profondità: query specifiche sulle domande chiave del tema
3. Contraddizioni: "Ci sono posizioni contrastanti nelle fonti?"
4. Actionable: "Quali sono i passi concreti da applicare?"

```bash
notebooklm ask "<domanda>"
```

La risposta include citazioni `[1][2]` mappate alle sorgenti (visibili con `notebooklm source list`).

### Fase 6 — Salvare la sintesi in Obsidian

Generare una nota markdown con il template completo in [references/obsidian-note-template.md](references/obsidian-note-template.md).

Salvare in `<vault-path>/02-Ricerca/<tema>_YYYY-MM-DD.md` (o nel path configurato dall'utente).

### Fase 7 — Suggerire follow-up

Proporre all'utente:

- Generare artefatti aggiuntivi: `notebooklm generate audio`, `notebooklm generate mind-map`
- Re-query su sotto-temi emersi
- Aggiornare eventuali MOC (Map of Content) o indici nel vault

## Examples

### Esempio 1 — Research "Claude Skills best practices"

```bash
notebooklm create "Claude Skills Best Practices"
notebooklm use <id>
notebooklm source add "https://code.claude.com/docs/en/skills"
notebooklm source add "https://github.com/anthropics/skills"
notebooklm source add "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
# ... altre 5-10 sorgenti
notebooklm ask "Quali sono i 5 principi di una description efficace?"
```

Salvataggio sintesi in `<vault-path>/02-Ricerca/claude-skills-best-practices_2026-04-24.md`.

### Esempio 2 — Analisi di 5 video YouTube di un canale

```bash
notebooklm create "Topic X — video analysis"
notebooklm source add "<youtube_url_1>"
# ... altri URL
notebooklm ask "Quali sono i 3 casi d'uso più ricorrenti nei video?"
```

## Gotchas

- Mai analizzare YouTube senza NotebookLM: senza trascritti reali il modello allucina contenuto. NotebookLM fornisce i trascritti veri indicizzati.
- L'indicizzazione richiede tempo: non porre query prima che tutte le sorgenti siano `ready`, altrimenti le risposte sono incomplete.
- Limite free: circa 50 sorgenti per notebook. Per tematiche più ampie, creare notebook separati invece di uno generico.
- Paywall genera errori: articoli Medium o Substack dietro paywall falliscono. Sostituire con alternative pubbliche o versioni archiviate.
- Un notebook per tema coerente: NotebookLM risponde meglio con 10 sorgenti omogenee che con 50 eterogenee. Preferire notebook focalizzati.
- Notebook effimero, vault persistente: il notebook esiste su server Google, il vault Obsidian è controllato dall'utente. Salvare sempre la sintesi nel vault.
- Il `notebook_id` va riportato nel frontmatter della nota Obsidian per tracciabilità e possibili re-query future.
- Scope discipline: questa skill produce ricerca grounded multi-sorgente con citazioni. Per query web semplici senza citazioni, usare direttamente i tool di ricerca standard; NotebookLM introduce overhead (indicizzazione, CLI) che non è giustificato se basta una risposta rapida senza rigor accademico.

## References

- [references/notebooklm-cli-commands.md](references/notebooklm-cli-commands.md): tutti i comandi CLI con esempi
- [references/obsidian-note-template.md](references/obsidian-note-template.md): template YAML+markdown per sintesi

---
_Basato su [docs Anthropic skills](https://code.claude.com/docs/en/skills), [NotebookLM CLI pubblico](https://github.com/wi11iam/notebooklm-cli). MIT License._
