# PARA Structure — Vault Obsidian

Struttura del vault basata sul metodo PARA ([Tiago Forte, "Building a Second Brain"](https://www.buildingasecondbrain.com/)) adattato con Zettelkasten (backlink bidirezionali).

## Contents

- [Cartelle root](#cartelle-root)
- [Regole per categoria](#regole-per-categoria)
- [Naming convention](#naming-convention)
- [Frontmatter YAML universale](#frontmatter-yaml-universale)
- [Backlink convention](#backlink-convention)
- [Tag convention](#tag-convention)
- [Indici _INDEX.md](#indici-_indexmd)
- [Ricerca nel vault](#ricerca-nel-vault)
- [Anti-pattern](#anti-pattern)

## Cartelle root

Struttura standard (il path base `<vault-path>` è configurabile):

```text
<vault-path>/
├── 01 - Progetti/       # progetti attivi, con outcome chiaro
├── 02 - Ricerca/        # ricerca con fonti, note grounded, research-log
├── 03 - Archivio/       # progetti conclusi (read-only)
├── 04 - Clienti/        # anagrafica cliente (no PII)
├── 05 - Risorse/        # risorse riutilizzabili (SOP, template, checklist)
├── 06 - Original/       # pensiero originale dell'utente (opzionale)
└── _INDEX.md            # indice master
```

La cartella `06 - Original/` è opzionale e rappresenta il pensiero originale dell'utente (insight, framework propri, concetti generalizzati). È protetta: Claude propone ma non scrive senza conferma esplicita.

## Regole per categoria

### 01 - Progetti

- Quando: esiste un progetto attivo con outcome misurabile
- Frontmatter `type`: `progetto`
- `status`: `attivo`, `pausa`, `concluso`

### 02 - Ricerca

- Quando: ricerca profonda, output NotebookLM, analisi tool/repo, research-log
- Frontmatter `type`: `ricerca` o `research-log`
- `source`: `ai`, `notebooklm`, `web`, `interview`

### 03 - Archivio

- Quando: il progetto è concluso (spostato da `01 - Progetti/`), si mantiene per reference
- Dopo l'archivio: solo letture, niente modifiche

### 04 - Clienti

- Quando: nuovo cliente rilevante o aggiornamento di contesto
- No PII: solo ruolo, azienda, settore, contesto relazione
- Non inserire email, telefoni o nomi completi in chiaro

### 05 - Risorse

- Quando: workflow ripetibile, SOP, template, checklist
- Il contenuto deve essere generalizzabile (non project-specific)

### 06 - Original

- Cartella sacra: mai scrivere senza approvazione dell'utente
- Pattern di proposta: "Ho notato un pattern X. Propongo bozza `06 - Original/pattern-x.md`. Approva?"
- Solo l'utente decide cosa merita di stare qui

## Naming convention

```text
<argomento-concreto-kebab-case>_YYYY-MM-DD.md
```

Esempi validi:

- `claude-skills-design_2026-04-24.md`
- `gtm-pattern_2026-03-15.md`

Esempi da evitare:

- `note.md` (argomento assente)
- `ClaudeSkillsDesign.md` (CamelCase, senza data)

## Frontmatter YAML universale

```yaml
---
created: YYYY-MM-DD
type: <progetto | ricerca | research-log | cliente | risorsa | original>
source: <ai | notebooklm | web | interview | user>
status: <attivo | archiviato | pausa>
tags: [<tag-principale>, source/<source>, <altri-tag>]
---
```

## Backlink convention

Ogni nota dovrebbe linkare 2-5 note correlate. Pattern:

- Nota ricerca → link ai progetti dove è stata usata
- Nota progetto → link ai clienti coinvolti + ricerche applicate
- Nota cliente → link ai progetti attivi con quel cliente
- Nota Original → link alle ricerche e ai progetti che hanno ispirato il pensiero

Non creare note vuote solo per avere un link: aspettare che la nota target abbia contenuto reale.

## Tag convention

Obbligatori per tracciabilità:

- `source/ai` — contenuto AI-generato
- `source/notebooklm` — da NotebookLM con citazioni
- `source/user` — scritto direttamente dall'utente
- `source/mixed` — ibrido (AI suggerisce, user edita)

Opzionali per topic:

- `topic/<area>` (es. `topic/gtm`, `topic/ai-agents`)
- `cliente/<nome>` (es. `cliente/acme-corp`)

## Indici _INDEX.md

Ogni cartella root può avere un `_INDEX.md` con:

- Lista delle note organizzate (alfabetica o per status)
- Note recenti (ultimi 7 giorni)
- TODO (note da completare o da espandere)

Aggiornare manualmente dopo aggiunte rilevanti (> 3 note), oppure tramite script.

## Ricerca nel vault

Cercare nel vault PRIMA di ogni ricerca esterna (evita duplicazione):

```bash
# Per contenuto
grep -r "<keyword>" "<vault-path>/02 - Ricerca/"

# Per tag
grep -rl "topic/<area>" "<vault-path>/"

# Per status
grep -rl "status: attivo" "<vault-path>/01 - Progetti/"
```

## Anti-pattern

- Sottocartelle nidificate: il vault è piatto per singola categoria, max 1 livello dopo la root
- Note senza frontmatter: se una nota non ha YAML, non è una nota valida
- Duplicati: stesso tema in 2 note separate = va fatto refactor (merge)
- PII nelle note cliente: email, telefoni, nomi completi sono vietati
- Scrivere in `06 - Original/` senza approvazione: viola la proprietà del pensiero dell'utente

## Rituali consigliati

- Settimanale: review `02 - Ricerca/` (completezza, backlink), review `01 - Progetti/` (status update, archive concluded)
- Mensile: cleanup duplicati, review `06 - Original/` per aggiungere backlink
- Annuale: archive progetti inattivi > 6 mesi, refactor della taxonomy se evoluta

---
_Metodo PARA: [Tiago Forte](https://fortelabs.com/blog/para/). Zettelkasten: [Sönke Ahrens, "How to Take Smart Notes"](https://takesmartnotes.com/)._
