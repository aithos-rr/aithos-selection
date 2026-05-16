# Obsidian note template — research

Template completo per salvare una sintesi NotebookLM in un vault Obsidian. Frontmatter YAML + struttura markdown + convenzioni di linking.

## Contents

- [Template completo](#template-completo)
- [Convenzioni dei campi frontmatter](#convenzioni-dei-campi-frontmatter)
- [Naming convention](#naming-convention)
- [Backlink strategy](#backlink-strategy)
- [Come aggiornare MOC e indici](#come-aggiornare-moc-e-indici)
- [Research log per fallimenti o insight inattesi](#research-log-per-fallimenti-o-insight-inattesi)

## Template completo

```markdown
---
created: 2026-04-24
type: ricerca
source: notebooklm
notebook_id: <id-restituito-da-notebooklm-create>
status: attivo
tags: [ricerca, source/notebooklm, <tag-tematico>]
---

# <Titolo ricerca descrittivo>

## Contesto

Breve paragrafo (2-4 righe) che descrive il tema, il perché della ricerca, e l'outcome atteso.

## Query eseguite

1. <domanda 1>
2. <domanda 2>
3. <domanda 3>

## Sintesi

<Risposta sintetizzata dalle query, con citazioni inline [1][2] mantenute>

### Sotto-tema A

<contenuto>

### Sotto-tema B

<contenuto>

## Conclusioni

- <Takeaway 1 actionable>
- <Takeaway 2 actionable>
- <Takeaway 3 actionable>

## Contraddizioni nelle fonti

<Se emerse dalle query, elencare le posizioni contrastanti>

## Fonti citate

1. [<titolo>](<url>) — perché è rilevante
2. [<titolo>](<url>) — perché è rilevante
3. ...

## Backlinks

- [[NotaCorrelata1]]
- [[NotaCorrelata2]]

## Next steps

- [ ] Aggiornare MOC o indice tematico
- [ ] Re-query su <sotto-tema> se necessario
- [ ] Generare mind-map con `notebooklm generate mind-map`
```

## Convenzioni dei campi frontmatter

- `created`: data ISO `YYYY-MM-DD`, data di creazione della nota
- `type`: `ricerca` per note di ricerca; altri valori comuni nel vault PARA sono `progetto`, `cliente`, `risorsa`, `research-log`
- `source`: origine della sintesi (`notebooklm`, `web-search`, `interview`, `internal-doc`)
- `notebook_id`: ID NotebookLM per tracciabilità e re-query future
- `status`: `attivo`, `archiviato`, `in-review`
- `tags`: array di tag hierarchical con prefisso `source/` per la provenienza

## Naming convention

Il nome file deve seguire il pattern:

```text
<argomento-kebab-case>_YYYY-MM-DD.md
```

Esempi:

- `claude-skills-best-practices_2026-04-24.md`
- `gtm-saas-b2b_2026-04-20.md`
- `competitor-analysis-q2_2026-03-15.md`

## Backlink strategy

- Linkare verso note già esistenti con `[[NomeNota]]`
- Creare i backlink anche da note correlate verso questa nota (bidirezionale)
- Se si introduce un concetto nuovo non presente nel vault, NON creare una nota vuota solo per il link: aspettare che ci sia contenuto reale

## Come aggiornare MOC e indici

Se la ricerca tocca un tema che ha un MOC (Map of Content) nel vault, aggiungerci il link alla nota appena creata. Se il tema non ha ancora un MOC e sono 3+ note correlate, proporre all'utente di crearne uno.

## Research log per fallimenti o insight inattesi

Se durante la ricerca emerge un approccio sbagliato, una sorgente inaffidabile, o un insight inatteso, creare ANCHE un research-log nella stessa cartella:

```markdown
---
created: 2026-04-24
type: research-log
tags: [research-log, source/ai]
status: attivo
---

# <Titolo breve>

**Cosa ho provato**: <descrizione>
**Cosa è andato storto** (o inaspettato): <descrizione>
**Cosa ha risolto**: <descrizione>
**Lezione per il futuro**: <una frase>
```

Questo permette di accumulare memoria evolutiva tra sessioni diverse senza dover rileggere ogni note di ricerca.

---
_Fonte struttura PARA: [Building a Second Brain — Tiago Forte](https://www.buildingasecondbrain.com/). Adattato alla convenzione Obsidian._
