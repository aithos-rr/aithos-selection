---
name: "obsidian-brain"
description: "Salva ricerca, decisione strategica o research log in un vault Obsidian applicando la struttura PARA (01-Progetti / 02-Ricerca / 04-Clienti / 05-Risorse) con frontmatter YAML e backlink [[NomeNota]]. Da attivare quando l'utente dice \"salva in Obsidian\", \"metti nel vault\", \"archivia ricerca\", \"research log\", \"secondo cervello\"; oppure quando una sessione produce output markdown oltre 300 parole con fonti citate o una decisione esplicita (\"ok, usiamo X invece di Y\"). Rispetta le regole: no PII nelle note cliente, vault piatto, verifica duplicati prima di scrivere, chiede conferma per la cartella `06 - Original/`."
when_to_use: "Parole chiave \"Obsidian\", \"vault\", \"secondo cervello\", \"research log\", \"salva ricerca\", \"archivia\"; output sessione oltre 300 parole con citazioni; decisione architetturale esplicita da preservare"
allowed-tools: "Read Write Edit Glob Grep Bash(find:*) Bash(ls:*)"
---
# Obsidian Brain

Skill che fa agire Claude come "bibliotecario" del vault Obsidian applicando struttura PARA e backlink Zettelkasten. Il vault è un secondo cervello persistente: ogni nota deve avere valore oltre la sessione corrente.

Il path del vault (`<vault-path>`) è configurato dall'utente una volta e usato da tutta la skill. Default suggerito: `~/Documents/Obsidian/<nome-vault>/`.

## When to use

Attivare quando:

- Ricerca significativa (web, NotebookLM, analisi tool/repo) → `02 - Ricerca/`
- Decisione strategica (stack, architettura, approccio) → `01 - Progetti/`
- Nuovo contatto o cliente rilevante → `04 - Clienti/` (no PII, solo ruolo e contesto)
- Concetto riutilizzabile generalizzato → `06 - Original/` (proporre, non scrivere senza conferma)
- Workflow ripetibile o SOP → `05 - Risorse/`
- Research log (errore + fix, successo inaspettato) → `02 - Ricerca/` con `type: research-log`

Non attivare se:

- Task banale, fix minore, operazione di routine
- Il contenuto è già nel vault (aggiornare la nota esistente, non duplicare)
- L'informazione vale solo per la sessione corrente (usare plan o task, non memoria)

## Vault structure

Struttura root del vault (dettaglio in [references/para-structure.md](references/para-structure.md)):

```text
<vault-path>/
├── 01 - Progetti/
├── 02 - Ricerca/
├── 03 - Archivio/
├── 04 - Clienti/
├── 05 - Risorse/
├── 06 - Original/       # cartella sacra: solo con approvazione utente
└── _INDEX.md
```

## Instructions

### Fase 1 — Decidere se scrivere

Applicare il test "valore oltre la sessione":

- La nota sarà utile in futuro?
- Esiste già nel vault?
- È pensiero originale dell'utente?

Se c'è dubbio, chiedere via AskUserQuestion: "Salvo in Obsidian? In quale cartella?"

### Fase 2 — Verificare duplicati

Vedere [references/vault-operations.md](references/vault-operations.md) per i comandi di search e dedup.

Sintesi:

```bash
grep -r "<keyword>" "<vault-path>/02 - Ricerca/"
```

Se trovata nota esistente → aggiornarla in append, non creare duplicato.

### Fase 3 — Creare la nota con template appropriato

Template disponibili:

- [assets/template-research.md](assets/template-research.md) per note di ricerca
- [assets/template-research-log.md](assets/template-research-log.md) per research-log
- Template progetto, cliente, risorsa → vedere [references/vault-operations.md](references/vault-operations.md)

Copiare il template, sostituire i placeholder, salvare nel path corretto.

### Fase 4 — Naming e path

Pattern: `<argomento-kebab-case>_YYYY-MM-DD.md`

Esempi:

- `claude-skills-design_2026-04-24.md`
- `gtm-pattern-b2b_2026-03-15.md`

Attenzione ai path con spazi (es. `02 - Ricerca/`): usare le virgolette o l'escape nei comandi shell.

### Fase 5 — Aggiornare indici

Se la cartella di destinazione contiene `_INDEX.md`, aggiungere il link alla nuova nota.

### Fase 6 — Backlink check

Proporre backlink verso:

- Note esistenti su clienti o progetti menzionati
- Cartella `06 - Original/` se la nota estende un concetto già presente (solo proposta, non scrittura diretta)

## Examples

### Esempio 1 — Salvare research NotebookLM

Dopo una sessione NotebookLM:

```bash
# Verificare duplicati
grep -r "Claude Skills" "<vault-path>/02 - Ricerca/"
# Nessun match → nuova nota
```

Creare `<vault-path>/02 - Ricerca/claude-skills-best-practices_2026-04-24.md` con `type: ricerca`, `source: notebooklm`, `notebook_id: <id>`. Backlink a `[[ProgettoFormazione]]` se rilevante.

### Esempio 2 — Research log su errore

Sessione in cui è emerso un pattern sbagliato e il fix:

Creare `<vault-path>/02 - Ricerca/<tema>_2026-04-24.md` con `type: research-log`. Lezione sintetizzata in una frase.

### Esempio 3 — Concetto per cartella Original (solo proposta)

Durante una sessione emerge un pattern generalizzabile. La skill NON scrive in `06 - Original/`, ma propone all'utente:

> "Questo pattern 'X' sembra materia per `06 - Original/`. Vuoi che proponga una bozza `06 - Original/pattern-x.md` da rivedere insieme prima di salvarla?"

## Gotchas

- Cartella `06 - Original/` è sacra: mai scrivere senza approvazione esplicita. È il pensiero originale dell'utente.
- No PII nelle note cliente: mai email, telefoni, nomi completi in chiaro. Solo ruoli, aziende, contesto.
- No sovrascrittura di note umane: se una nota esiste con modifiche utente, aggiornare in append.
- Vault piatto: no sottocartelle oltre il primo livello dopo la root. Categorie sono già le cartelle root numerate.
- Verifica duplicati ogni volta: due note sullo stesso tema = vault spezzato. Merge sempre quando possibile.
- Path con spazi nei comandi shell: usare virgolette. `"<vault-path>/02 - Ricerca/"`, non `<vault-path>/02 - Ricerca/` senza quote.
- Frontmatter obbligatorio: se la nota non ha YAML valido, non è una nota conforme e va corretta prima del save.
- Scope discipline: questa skill gestisce note di valore persistente (valore oltre la sessione). Per output effimeri (task list della sessione, plan intermedi, note di lavoro temporanee) usare il contesto della conversazione o i plan file di Claude Code, non scrivere nel vault.

## References

- [references/para-structure.md](references/para-structure.md): filosofia PARA, regole per categoria, tag convention
- [references/vault-operations.md](references/vault-operations.md): operazioni (search, dedup, backlink, index update) con esempi shell
- [assets/template-research.md](assets/template-research.md): template per nota di ricerca
- [assets/template-research-log.md](assets/template-research-log.md): template per research-log

---
_Metodo PARA: [Tiago Forte](https://fortelabs.com/blog/para/). Zettelkasten: [Sönke Ahrens](https://takesmartnotes.com/). MIT License._
