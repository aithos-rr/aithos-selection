---
name: n8n-quickstart
description: Costruisce workflow n8n partendo da una descrizione in linguaggio business (non tecnico). Da attivare quando l'utente dice "automatizza questo su n8n", "crea un workflow che...", "voglio connettere X e Y", "automazione no-code". Wrapper amichevole per non-developer che usa sotto il cofano le 7 skill n8n di czlonkowski/n8n-skills (upstream MIT). Traduce concetti tecnici (Code node, expression, webhook, credentials) in linguaggio business. Include 3 ricette pronte (lead gen, email nurture, social monitoring).
when_to_use: Automazione workflow, connessione tool, n8n, lead gen automation, email nurture, social monitoring, pipeline dati no-code
argument-hint: "<descrizione-automazione>"
allowed-tools: Read Write Edit Grep Glob
---

# n8n Quickstart

Wrapper per utenti non-developer che vogliono costruire workflow n8n con Claude Code. Non reinventa le 7 skill n8n di [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills), ma le eleva:

1. Traduce linguaggio business in workflow n8n
2. Fornisce 3 ricette pronte (lead gen, email nurture, social monitor)
3. Guida setup MCP passo-passo
4. Produce un CLAUDE.md del progetto n8n pre-compilato

## When to use

Attivare quando:

- L'utente descrive un'automazione: "ogni mattina manda email riassuntiva", "quando arriva un lead, fai X"
- Vuole connettere 2+ tool business (Gmail, Slack, CRM, Sheets, HubSpot)
- Parla di "automazione no-code"
- Ha n8n già attivo (self-hosted, cloud, o desktop) e vuole orchestrarlo con Claude

Non attivare se:

- n8n non è nello stack dell'utente (proporre alternativa: scheduled tasks di Claude Code)
- Task one-shot, non ripetibile
- Serve codice custom pesante (scaffolding di un progetto è meglio di un workflow)

## Prerequisiti

Il partecipante deve avere:

1. n8n attivo (cloud, self-hosted, o desktop)
2. n8n-mcp server installato ([guida ufficiale czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp))
3. Le 7 skill upstream czlonkowski installate:

    ```text
    /plugin marketplace add czlonkowski/n8n-skills
    /plugin install n8n-skills@n8n-skills
    ```

Se qualcosa manca, la skill stampa le istruzioni di setup e termina.

## Instructions

### Fase 1 — Scoprire l'intento

Chiedere all'utente via AskUserQuestion:

1. Cosa automatizzare? (descrizione 1-2 frasi in linguaggio business)
2. Da dove parte? (trigger: cron schedulato, webhook evento, manuale)
3. Cosa produce? (output: email, record CRM, messaggio Slack, Sheet aggiornato)
4. Quali tool connettere? (lista)

Se la descrizione è troppo ampia ("tutto quello che so"), chiedere di focalizzarsi su un singolo use case concreto.

### Fase 2 — Match con una ricetta

Verificare se l'intento matcha una delle 3 ricette in [references/recipes.md](references/recipes.md):

- Lead Gen Pipeline: nuovo lead → enrichment → scoring → CRM + trigger outreach
- Email Nurture Loop: criterio lead → sequenza email automatica con condizioni
- Social Monitor: keyword o competitor → analisi sentiment → report Slack/email

Se match → partire dalla ricetta. Altrimenti procedere alla Fase 3.

### Fase 3 — Pattern architettura

Usare la skill upstream `czlonkowski/n8n-workflow-patterns` per identificare quale dei 5 pattern si applica:

1. Webhook (risposta a eventi esterni)
2. HTTP API (servizio che risponde a richieste)
3. Database (sync o CRUD su DB)
4. AI Agent (Claude o altro LLM decide il prossimo step)
5. Scheduled (cron periodico)

### Fase 4 — Build del workflow

Usare `czlonkowski/n8n-mcp-tools-expert` per:

1. Cercare nodi rilevanti (`search_nodes`)
2. Configurare i nodi (`get_node_info`, `validate_node`)
3. Creare il workflow (`create_workflow`)
4. Validare (`validate_workflow` profilo `runtime`)

Mentre si costruisce, tradurre in linguaggio business (dettaglio completo in [references/business-jargon-mapping.md](references/business-jargon-mapping.md)):

- Code node → "trasforma i dati in formato X"
- Expression → "formula (come in Excel)"
- Webhook → "endpoint che riceve notifiche"
- Credentials → "accesso al tuo account del servizio X"

### Fase 5 — Setup CLAUDE.md del progetto

Generare o aggiornare `<progetto>/CLAUDE.md` con il template in [references/claude-md-n8n-template.md](references/claude-md-n8n-template.md).

### Fase 6 — Test e deploy

1. Test manuale: eseguire il workflow con un dato di test, verificare l'output
2. Dry run: se tocca produzione (CRM, email) usare modalità sandbox prima
3. Activate: attivare il trigger cron o webhook solo dopo test OK
4. Monitor dei primi run: verificare le prime 5-10 esecuzioni reali

### Fase 7 — Troubleshooting

In caso di errori, invocare `czlonkowski/n8n-validation-expert` per interpretare i messaggi e suggerire fix.

## Examples

### Esempio 1 — Report settimanale schedulato

Intent: "ogni lunedì alle 9 manda un report settimanale via email al team".

Pattern: Scheduled (nessuna ricetta, è semplice).

Workflow:

1. Cron trigger (lunedì 09:00)
2. HTTP request verso l'API del CRM (lead nuovi della settimana)
3. Code node per formattazione Markdown
4. Gmail send al team

CLAUDE.md del progetto: descrive il trigger, l'endpoint CRM, il formato atteso.

### Esempio 2 — Lead enrichment pipeline

Intent: "quando arriva un lead da Typeform, arricchiscilo e mettilo nel CRM".

Ricetta: Lead Gen Pipeline (match).

Workflow (pre-costruito nella ricetta):

1. Webhook trigger (Typeform submit)
2. HTTP request verso provider di enrichment (email verify, company data)
3. Code node per scoring
4. Nodo CRM → create record
5. Slack alert se lo scoring supera una soglia

### Esempio 3 — Social monitoring

Intent: "monitora le menzioni del mio brand su LinkedIn, alert se sentiment negativo".

Ricetta: Social Monitor (match).

Workflow:

1. Cron (ogni 4 ore)
2. Apify LinkedIn scraper via HTTP
3. AI Agent (LLM) per sentiment analysis e categorizzazione
4. Google Sheet append
5. Slack alert solo se menzione negativa

## Gotchas

- n8n Python ha limiti: no librerie esterne (no requests, pandas, numpy). Per il 95% dei casi usare JavaScript nel Code node. Fonte: `czlonkowski/n8n-code-python`.
- Webhook data location: sempre `$json.body`, mai `$json` diretto. Errore classico.
- Code node return format: deve essere `[{json: {...}}]`, non `{...}` diretto.
- Credentials: mai hardcoded di API key nel Code node. Usare sempre il credentials manager di n8n.
- Rate limit: ogni servizio ha i suoi limiti. Aggiungere un nodo `Wait` o retry logic per evitare errori 429.
- nodeType format: distinguere `nodes-base.*` da `n8n-nodes-base.*`. Errore comune quando si creano workflow programmaticamente.
- Validation profile: usare `runtime` durante lo sviluppo, `strict` prima di attivare in produzione.
- Template > scratch: n8n ha una libreria di template ufficiali molto ampia ([n8n.io/workflows](https://n8n.io/workflows)). Controllare sempre prima di costruire da zero.
- Scope discipline: questa skill costruisce workflow n8n. Per scripting one-shot senza orchestrazione (script bash, Python ad-hoc, comandi terminal), Claude Code scrive direttamente senza invocare questa skill. n8n introduce complessità di setup che si giustifica solo con workflow ricorrenti.

## References

- [references/recipes.md](references/recipes.md): 3 ricette complete (Lead Gen, Email Nurture, Social Monitor)
- [references/business-jargon-mapping.md](references/business-jargon-mapping.md): 30 traduzioni tech → business per spiegare workflow
- [references/claude-md-n8n-template.md](references/claude-md-n8n-template.md): template CLAUDE.md per progetti n8n

Skill upstream (requisito): [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills) — 7 skill complementari MIT, maintainer Romuald Członkowski.

---
_Wrapper su [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills). Basato su [docs Anthropic skills](https://code.claude.com/docs/en/skills). MIT License._
