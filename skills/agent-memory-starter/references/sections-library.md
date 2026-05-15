# Sections Library — 15 sezioni opzionali per CLAUDE.md

Libreria di sezioni riutilizzabili con criteri di inclusione e template pronti. Ogni sezione è autonoma e copiabile nel CLAUDE.md generato dal wizard.

## Contents

- [Obsidian second brain](#obsidian-second-brain)
- [NotebookLM research stack](#notebooklm-research-stack)
- [Skill pack installato](#skill-pack-installato)
- [Routing MCP server](#routing-mcp-server)
- [Privacy e dati sensibili](#privacy-e-dati-sensibili)
- [Engineering preferences](#engineering-preferences)
- [Quando le cose vanno male](#quando-le-cose-vanno-male)
- [Research log](#research-log)
- [Tone e persona](#tone-e-persona)
- [Progetti attivi](#progetti-attivi)
- [Modalità operative](#modalita-operative)
- [Stack operativo](#stack-operativo)
- [Note operative](#note-operative)
- [Git e commit conventions](#git-e-commit-conventions)
- [Deploy e ambienti](#deploy-e-ambienti)

## Obsidian second brain

Quando includere: l'utente usa Obsidian come knowledge base e vuole che Claude scriva note in modo strutturato.

```markdown
## Obsidian second brain

Vault: `<path-del-vault>`. Struttura PARA (01-Progetti, 02-Ricerca, 04-Clienti, 05-Risorse).

Quando scrivere nel vault:
- Ricerche significative → `02 - Ricerca/`
- Decisioni strategiche (stack, architettura) → `01 - Progetti/`
- Nuovo contatto/cliente → `04 - Clienti/` (no PII)
- Workflow ripetibili → `05 - Risorse/`

Naming: `argomento_YYYY-MM-DD.md`. Frontmatter YAML con `created`, `type`, `source`, `status`, `tags`. Backlink `[[NomeNota]]`. Tag `#source/ai` per trasparenza.
```

## NotebookLM research stack

Quando includere: l'utente fa ricerca approfondita su documentazioni tecniche, video YouTube, o >50 fonti.

```markdown
## NotebookLM — Research grounded

CLI: `notebooklm` (https://github.com/wi11iam/notebooklm-cli). Usare obbligatoriamente per:
- Video YouTube (anti-allucinazione trascritti)
- Documentazioni tecniche nuove
- Volumi grandi di fonti con citazioni verificabili

Flusso: `notebooklm create` → `source add` → attendere 3 min indicizzazione → `ask` con risposte citate.
```

## Skill pack installato

Quando includere: l'utente ha installato uno skill pack specifico e vuole che Claude sappia quali skill sono disponibili.

```markdown
## Skill pack attivi

- `/skill-builder` — wizard creazione skill
- `/skill-reviewer` — audit qualità skill
- `/research-notebook` — ricerca grounded NotebookLM
- `/obsidian-brain` — gestione vault Obsidian
- `/n8n-quickstart` — workflow n8n da descrizione business
```

## Routing MCP server

Quando includere: l'utente lavora con molti tool e vuole che Claude scelga sempre il tool giusto senza chiedere.

```markdown
## Stack operativo — routing

- Campagne email → <tool scelto>
- CRM e contatti → <tool scelto>
- Automazione workflow → <tool scelto>
- Ricerca web / scraping → <tool scelto>
- Visualizzazione flussi → <tool scelto>
```

## Privacy e dati sensibili

Quando includere: l'utente lavora con dati PII, GDPR, o clienti esterni.

```markdown
## Privacy e dati sensibili

- Non esporre PII (email, telefoni, nomi) in chiaro quando non necessario
- Chiedere conferma prima di bulk export da CRM o campagne
- Dati EU → GDPR si applica
- Se mostri dati di lead, anonimizza o mostra solo un sample
```

## Engineering preferences

Quando includere: l'utente scrive o revisiona codice.

```markdown
## Engineering Preferences

- DRY: flagga ripetizioni aggressivamente
- Test: meglio troppi che troppo pochi
- Bilanciamento "engineered enough": no fragile, no premature abstraction
- Esplicito > furbo
- Commenti solo dove la logica non è auto-evidente
- No-code first quando esistono alternative adatte
```

## Quando le cose vanno male

Quando includere: sempre utile, evita stalli.

```markdown
## Quando le cose vanno male

1. Se un MCP server non risponde → 1 tentativo, poi avvisa e suggerisci alternativa
2. Se il codice non compila → fix immediato, non aspettare richiesta
3. Se serve competenza esterna → avvisa subito
4. Se sei bloccato → cambia strada, non insistere
5. Se puoi rompere roba in produzione → fermati e chiedi
```

## Research log

Quando includere: l'utente vuole memoria evolutiva fra sessioni.

```markdown
## Research Log

Quando qualcosa fallisce, viene corretto, o produce un risultato inaspettato, scrivi una nota in `02 - Ricerca/` con frontmatter:

type: research-log, tags: [research-log, #source/ai], status: attivo

Struttura: Cosa ho provato → Cosa è andato storto → Cosa ha risolto → Lezione.
```

## Tone e persona

Quando includere: l'utente ha uno stile di comunicazione preciso.

```markdown
## Persona

Tono: [diretto / formale / casual / tecnico]. Zero giri di parole.

- Se una richiesta è poco chiara → chiedi in 1 riga
- Mostra 2-3 approcci con tradeoff quando rilevante
- Codice production-ready, zero over-engineering
- No meta-commenti su "essere una AI"
```

## Progetti attivi

Quando includere: sempre, aiuta Claude a contestualizzare.

```markdown
## Progetti attivi

- **<Nome progetto 1>**: <ruolo / cosa fai / stakeholder>
- **<Nome progetto 2>**: <ruolo / cosa fai / stakeholder>
```

## Modalità operative

Quando includere: l'utente vuole switchare tra stili di lavoro.

```markdown
## Modalità operative

### Execute mode (default)
Vai dritto al punto. Minima spiegazione.

### Review mode (attiva con `/review`)
Analisi strutturata. Per ogni issue: problema → opzioni → raccomandazione → conferma.

### Learn mode
Spiega cosa fai e perché. Usa analogie pratiche.
```

## Stack operativo

Quando includere: l'utente usa molti tool e vuole routing automatico.

```markdown
## Stack operativo

| Area | Tool | Note |
|------|------|------|
| CRM | <tool> | <uso> |
| Email | <tool> | <uso> |
| Workflow | <tool> | <uso> |
```

## Note operative

Quando includere: preferenze di lavoro generali non coperte altrove.

```markdown
## Note operative

- Preferisco MVP rapidi > piani perfetti
- Lavoro su più progetti contemporaneamente → non assumere contesto unico
- [Altre note specifiche del ruolo]
```

## Git e commit conventions

Quando includere: l'utente lavora con repo condivisi.

```markdown
## Git conventions

- Branch naming: <convenzione>
- Commit message: <convenzione o conventional commits>
- PR description: include contesto, test plan, rollback plan
- No force push su branch condivisi
```

## Deploy e ambienti

Quando includere: l'utente fa deploy su staging/prod.

```markdown
## Deploy

- Staging: <url o ambiente>
- Prod: <url o ambiente>
- Pre-deploy checklist: env vars, secret, build, smoke test
- Chi approva deploy in prod: <persona / ruolo>
```

---
_Fonte struttura CLAUDE.md: [docs Anthropic memory](https://code.claude.com/docs/en/memory). Template MIT License._
