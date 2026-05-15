# Vault operations — guida operativa

Operazioni ricorrenti sul vault Obsidian: search, dedup, naming, backlink, index. Tutti i path usano `<vault-path>` parametrizzato.

## Contents

- [Search nel vault](#search-nel-vault)
- [Duplicate check workflow](#duplicate-check-workflow)
- [Template aggiuntivi](#template-aggiuntivi)
- [Update degli indici _INDEX.md](#update-degli-indici-_indexmd)
- [Backlink strategy](#backlink-strategy)
- [Rituali settimanali e mensili](#rituali-settimanali-e-mensili)
- [Troubleshooting](#troubleshooting)

## Search nel vault

Comandi base per trovare contenuto esistente prima di creare una nuova nota:

```bash
# Per keyword in contenuto
grep -r "<keyword>" "<vault-path>/02 - Ricerca/"

# Per tag
grep -rl "topic/<area>" "<vault-path>/"

# Per status
grep -rl "status: attivo" "<vault-path>/01 - Progetti/"

# Per tipo di nota
grep -rlE "^type: ricerca" "<vault-path>/"

# Per data (note recenti, ultimi 7 giorni)
find "<vault-path>" -name "*.md" -mtime -7
```

## Duplicate check workflow

Prima di creare una nuova nota, applicare questo flusso:

1. Estrarre 2-3 keyword dal tema della nota
2. Cercare ogni keyword in `<vault-path>/02 - Ricerca/` e `<vault-path>/01 - Progetti/`
3. Se esiste una nota con lo stesso tema:
   - Aprirla e leggerne il contenuto
   - Valutare se è da aggiornare (append) o riscrivere (con backup)
   - Non creare duplicati "parziali"
4. Se non esiste, procedere con la creazione

Esempio comando per dedup:

```bash
for kw in "claude skills" "skill design"; do
    echo "=== $kw ==="
    grep -rl "$kw" "<vault-path>/02 - Ricerca/" | head -5
done
```

## Template aggiuntivi

Oltre ai template già in `assets/` (research, research-log), questi sono i pattern per le altre categorie.

### Template Progetto (01 - Progetti)

```markdown
---
created: YYYY-MM-DD
type: progetto
status: <attivo | pausa | concluso>
cliente: <nome-cliente>
tags: [progetto, cliente/<nome>]
---

# <Nome progetto>

## Contesto

Breve descrizione del progetto e del perché esiste.

## Obiettivo

Outcome misurabile e scadenza.

## Stack e stato corrente

Tool, tecnologie, milestone raggiunti e pending.

## Decisioni chiave

- YYYY-MM-DD: <decisione + motivazione>
- YYYY-MM-DD: <decisione + motivazione>

## Backlinks

- [[ClienteX]]
- [[RicercaCorrelata]]
```

### Template Cliente (04 - Clienti)

```markdown
---
created: YYYY-MM-DD
type: cliente
status: attivo
tags: [cliente]
---

# <Nome cliente / azienda>

## Contesto aziendale

Settore, dimensione, mercato geografico.

## Ruoli coinvolti

- <ruolo principale>: <area responsabilità, NO nome personale>
- <ruolo secondario>: <area responsabilità>

## Progetti attivi

- [[NomeProgetto1]]
- [[NomeProgetto2]]

## Touchpoint comunicazione

Tipo di relazione (email, call ricorrenti, on-demand).
NO email specifiche, NO telefoni.
```

### Template Risorsa (05 - Risorse)

```markdown
---
created: YYYY-MM-DD
type: risorsa
status: attivo
tags: [risorsa, <topic-tag>]
---

# <Nome risorsa>

## Cosa contiene

Breve descrizione del tipo di risorsa (SOP, template, checklist).

## Quando usarla

Trigger di attivazione.

## Contenuto

<Il contenuto della risorsa>

## Note di manutenzione

- Ultima revisione: YYYY-MM-DD
- Frequenza di aggiornamento prevista
```

## Update degli indici _INDEX.md

Se una cartella contiene un `_INDEX.md`, aggiornarlo dopo aver creato una nuova nota rilevante (> 3 note nuove dall'ultima revisione è soglia tipica).

Struttura consigliata per `_INDEX.md`:

```markdown
# <Categoria> — Index

## Recenti (ultimi 7 giorni)

- YYYY-MM-DD — [[NotaX]]
- YYYY-MM-DD — [[NotaY]]

## Per topic

### Topic A
- [[Nota1]]
- [[Nota2]]

### Topic B
- [[Nota3]]

## TODO (note da espandere)

- [ ] [[NotaBozzata]] — serve approfondimento X
```

## Backlink strategy

Ogni nota dovrebbe avere 2-5 backlink. Pattern per categoria:

| Categoria | Tipico backlink verso |
| --- | --- |
| Ricerca | Progetti dove è stata applicata, clienti rilevanti |
| Progetto | Clienti coinvolti, ricerche usate, risorse applicate |
| Cliente | Progetti attivi con quel cliente |
| Original | Ricerche e progetti che hanno ispirato il pensiero |

Non creare note vuote solo per creare il link. Se una nota target non esiste ancora, il link rimane "broken" (Obsidian lo evidenzia) finché non c'è contenuto reale.

## Rituali settimanali e mensili

### Settimanale (consigliato venerdì pomeriggio)

- Review `02 - Ricerca/`: completeness delle note settimana, backlink
- Review `01 - Progetti/`: status update, archive dei progetti conclusi
- Aggiornare `_INDEX.md` se sono state aggiunte > 3 note

### Mensile

- Cleanup duplicati: cercare note con tema simile e valutare merge
- Review `06 - Original/`: rileggere i pensieri e aggiungere backlink alle ricerche/progetti che li hanno ispirati
- Verificare tag orfani o inconsistenti

### Annuale

- Archive dei progetti inattivi > 6 mesi (spostare da `01 - Progetti/` a `03 - Archivio/`)
- Refactor della taxonomy se il lavoro dell'utente è evoluto

## Troubleshooting

### Problema: `grep` non trova una nota che so esistere

- Verificare encoding (UTF-8 standard, ma alcuni editor usano altri)
- Usare `grep -i` per case-insensitive
- Verificare path con spazi: le virgolette sono obbligatorie

### Problema: backlink non funziona

- Nome nota esatto richiesto: `[[NotaX]]` match "NotaX.md"
- No estensione `.md` nel backlink
- Obsidian risolve anche con path parziale se il nome è unico

### Problema: frontmatter non viene riconosciuto

- Deve iniziare con `---` sulla prima riga esatta (no whitespace prima)
- Chiusura `---` dopo i campi YAML
- Ogni campo è `chiave: valore` (spazio dopo `:`)

---
_Metodo PARA: [Tiago Forte](https://fortelabs.com/blog/para/). Riferimento Obsidian: [help.obsidian.md](https://help.obsidian.md)._
