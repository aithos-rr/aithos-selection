# CLAUDE.md template per progetti n8n

Copia questo template in `<progetto-n8n>/CLAUDE.md`. Compila i TODO.

```markdown
# <Nome progetto n8n>

Progetto di automazione workflow n8n per <obiettivo business 1 frase>.

## Contesto business

**Problema**: <cosa risolve>
**Output atteso**: <cosa produce, quanto spesso, per chi>
**Utenti**: <chi ne beneficia — team interno, clienti, ops>

## Workflow attivi

### Workflow 1: <nome>
- **Trigger**: <cron / webhook / manual>
- **Frequenza**: <daily 9am / on-event / ecc>
- **Output**: <Slack channel X / Sheet Y / Attio record Z>
- **File export**: `backend/workflows/workflow-1.json`

### Workflow 2: ...

## Credentials necessarie

<!-- NON mettere valori, solo lista -->
- [ ] Google OAuth (Sheets, Drive) — account: `<email>`
- [ ] Attio API key — salvato in n8n Credentials manager
- [ ] SmartLead API key
- [ ] Slack Webhook → `#<channel>`
- [ ] Parallel API key (per enrichment)

## Stack

- **n8n**: <cloud | self-hosted | desktop>, URL: `<url>`
- **Database** (se usato): <postgres / mysql / sqlite>
- **Deploy**: <server / docker / ngrok per test>

## Come lavoro con questo progetto

Sono <ruolo>, non developer. Capisco logica, non sintassi.
- Spiega ogni cambiamento in 1 riga di linguaggio business
- Prima di modificare workflow in prod, esegui in `runtime` (test)
- Se serve Code node, preferisci JavaScript (più stabile)
- Documenta gotcha incontrate in sezione apposita sotto

## Convenzioni

- Naming workflow: `<team>-<use-case>-<versione>` (es. `sales-lead-enrichment-v2`)
- Naming node: verbo + oggetto (es. "Fetch Lead from Attio")
- Comments su ogni nodo importante
- Variabili (sensitive) SOLO via Credentials manager, MAI hardcoded

## Monitoring

- **Dashboard health**: <URL>
- **Error Trigger workflow**: `ops-error-alert` invia a Slack `#ops-alerts`
- **Weekly report**: <giorno ora> genera report executions fallite

## Gotcha incontrate

<!-- Da compilare man mano -->
- `<data>`: <workflow X fallisce quando Y → fix: Z>
- ...

## Deploy checklist

Prima di attivare un workflow in prod:
- [ ] Testato con 5 input diversi in `runtime`
- [ ] Error Trigger collegato
- [ ] Credentials configurate (non hardcoded)
- [ ] Rate limit verificato sulle API esterne
- [ ] Rollback plan documentato
```

## Note applicative

- Questo CLAUDE.md vive in `<progetto>/CLAUDE.md` (project-level, non global)
- Aggiornalo dopo ogni nuovo workflow o gotcha incontrata
- Se il progetto ha SKILL.md specifiche (es. `/my-n8n-helpers`), linkale qui sotto "## Skill pack specifiche"
