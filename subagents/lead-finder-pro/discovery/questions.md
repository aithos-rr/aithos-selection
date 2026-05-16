# Discovery questions — `/lead-finder-pro`

> **8 domande** poste al first run via AskUserQuestion. Salvate in `<memory>/config.md` (project scope). Re-run skip se config presente — eccetto user dice "reconfigure" o equivalente.
>
> **Reference**: `ARCHITECTURE.md` sezione 2 + `DECISIONS.md` per logica.

## Format AskUserQuestion (per il system prompt)

Ogni domanda è un singolo `AskUserQuestion` con:

- `question`: testo italiano completo
- `header`: chip ≤12 char
- `options`: 2-4 options (esclusa "Other" automatica)
- `multiSelect`: false (tutte single-choice eccetto Q6 free-text)

## Q1 — Ruolo

```
question: "Qual è il tuo ruolo principale?"
header: "Ruolo"
options:
  - label: "Founder / CEO"
    description: "Ti occupi di GTM in prima persona, lead gen è una delle tue 5 priorità"
  - label: "SDR / BDR"
    description: "Lead gen + outreach è il tuo lavoro full-time"
  - label: "Marketing Manager"
    description: "Gestisci campagne e lead nurturing, coordini con sales"
  - label: "Freelancer GTM (Recommended)"
    description: "Consulente/agency che fa lead gen per clienti diversi"
```

**Conseguenza**: salva in `user.role`. Se Founder → tono executive, suggerisci batch piccoli (50-200). Se SDR/BDR → tono operational. Se Marketing → enfasi su segmentation. Se Freelancer → enfasi multi-progetto, suggerisci memory project per cliente.

## Q2 — Tool enrichment

```
question: "Quale tool di lead enrichment hai già attivo?"
header: "Enrichment"
options:
  - label: "Hunter (Recommended)"
    description: "Hunter ha MCP server nativo (mcp.hunter.io) — primo path"
  - label: "Apollo"
    description: "REST API ampia, attenzione bounce rate 15-25%"
  - label: "Clay"
    description: "Orchestrator multi-provider, costi credit imprevedibili"
  - label: "Nessuno (lo scelgo dopo)"
    description: "Suggerisco Hunter free tier per partire"
```

**Conseguenza**: salva in `stack.enrichment_primary`. Se Hunter → setup MCP `hunter`. Se Apollo → carica `references/apollo-api-recipes.md`. Se Clay → suggest "considera Hunter MCP come alternativa LLM-native". Se Nessuno → setup Hunter free tier guide.

## Q3 — CRM

```
question: "Quale CRM usi?"
header: "CRM"
options:
  - label: "Attio (Recommended se disponibile MCP)"
    description: "Attio MCP server permette sync nativo lead Hot"
  - label: "HubSpot"
    description: "Probe community MCP, fallback REST API"
  - label: "Pipedrive"
    description: "REST API, l'agente genera adapter custom"
  - label: "Salesforce"
    description: "REST + OAuth, adapter custom generato"
  - label: "Zoho CRM"
    description: "REST API, adapter custom"
  - label: "Notion DB (come CRM)"
    description: "Notion MCP community, sync via database row"
  - label: "Airtable (come CRM)"
    description: "REST API, adapter custom"
  - label: "Custom / altro"
    description: "Mi chiederai docs URL e API key, genero skill custom"
  - label: "Nessuno (CSV/Sheet only)"
    description: "Output Google Sheet o CSV locale, no sync CRM"
```

**Conseguenza**: salva in `stack.crm`. **Logica platform-agnostic**:

1. **Probe MCP** per il CRM scelto: cerca in `~/.claude.json`, `.mcp.json` project, MCP registry.
2. **Se MCP found** → use it directly (Attio nativo, Notion/HubSpot community se installato).
3. **Se MCP missing** → invoca skill `crm-adapter-generator`:
   - Studia API docs via WebFetch + context7
   - Genera skill adapter custom in `<memory>/skills-generated/<crm>/SKILL.md` + `adapter.py`
   - Registra env var richiesta in `<memory>/credentials.example.md`
   - Smoke test pre-attivazione
4. **Se Custom / altro** → chiedi docs URL + API key env var, poi flow step 3.
5. **Se Nessuno** → output CSV/Sheet mode, no push live.

**Default output mode** (post-detection): `push_live_record` direct nel CRM dell'utente. CSV diventa fallback solo se `crm=Nessuno` o adapter generation fallisce.

## Q4 — Outbound

```
question: "Quale tool outbound usi (email + LinkedIn)?"
header: "Outbound"
options:
  - label: "SmartLead (email)"
    description: "Chain con /outbound-orchestrator, esporta CSV ready import"
  - label: "HeyReach (LinkedIn)"
    description: "Multi-account distribution, importa via API"
  - label: "Lemlist / Instantly"
    description: "Esporta CSV + suggerisci import manuale"
  - label: "Manuale (Recommended se freelance)"
    description: "Output CSV ready, gestisci outreach a mano"
```

**Conseguenza**: salva in `stack.outbound`. Determinano output format finale + chain agent.

## Q5 — ICP description (free text)

```
question: "Qual è il tuo ICP? Settore + dimensione + geo. Esempio: 'SaaS B2B, 10-50 employees, USA + Europa'"
header: "ICP"
options: []  # free text via AskUserQuestion fallback "Other"
```

**Conseguenza**: salva in `icp.description`. **Auto-detect EU**: se contains keyword `EU`, `Europa`, `Italia`, `EMEA`, paesi EU (Germania, Francia, Spagna, ecc.) → `icp.geo_eu_detected = true` + `gdpr.mode_active = true` + warning "GDPR mode attivo" (DECISION-011).

## Q6 — Top 3 segmenti

```
question: "Quali sono i tuoi top 3 segmenti prioritari? (uno per riga)"
header: "Segmenti"
options: []  # free text 3 lines
```

**Conseguenza**: salva in `icp.segments` come lista. Usato per segmentation Fase 4.

## Q7 — Volume

```
question: "Quanti lead vuoi processare al mese?"
header: "Volume"
options:
  - label: "<50 (manuale è più rapido?)"
    description: "Sotto 50 lead/mese spesso conviene fare manualmente. Conferma scelta?"
  - label: "50-200 (Recommended sweet spot)"
    description: "Volume tipico per founder/freelancer GTM. Output Sheet + Hot leads in CRM"
  - label: "200-500"
    description: "Volume SDR/BDR full-time. Batch parallelo + checkpoint ogni 50 lead"
  - label: "500+"
    description: "Suggerisco Agent Teams parallelizzazione + monitoring CRM dedicato"
```

**Conseguenza**: salva in `preferences.monthly_volume`. Se <50 → conferma intent. Se 500+ → setup parallelization config.

## Q8 — Industry pattern scoring

```
question: "Quale pattern ICP scoring meglio rappresenta il tuo business?"
header: "Pattern"
options:
  - label: "SaaS B2B 60/40 fit/behavior (Recommended)"
    description: "Fit firmografico stabile, behavior signal alta velocità. Default 2026."
  - label: "Agency 50/50 fit/relationship"
    description: "Relationship signal pesa quanto il fit (introduzioni, network, brand fit)"
  - label: "eCommerce 70/30 firmografico"
    description: "Fit firmografico domina (industry, volume merchants), behavior secondario"
  - label: "Custom (definisco dopo)"
    description: "Carica template SaaS B2B 60/40 e personalizzalo in references/icp-scoring-framework.md"
```

**Conseguenza**: salva in `icp.industry_pattern` e `scoring.template`. Carica template corrispondente da `references/icp-scoring-framework.md` (DECISION-006).

## Logica conseguente — riepilogo

Dopo tutte 8 le domande, il subagent:

1. **Compila config.md completo** con tutti i field (vedi `ARCHITECTURE.md` sezione 6)
2. **Esegue MCP detection** (`mcp_detect.py`) e popola `mcp_available`/`mcp_fallbacks_active`
3. **Mostra summary** all'utente:

   ```
   Config salvata. Riepilogo:
   - Ruolo: Founder
   - Stack: Hunter (Enrichment) + Attio (CRM) + SmartLead (Outbound)
   - ICP: SaaS B2B 10-50 USA+EU → 🇪🇺 GDPR mode ATTIVO
   - Volume target: 50-200 lead/mese
   - Pattern scoring: SaaS B2B 60/40 fit/behavior
   - Tool disponibili: Hunter ✓, Attio ✓, Sheet ✓, Playwright ✓
   - Fallback attivi: Explorium → parallel-cli, HeyReach → CSV export

   Sono pronto. Dammi il tuo input lead (CSV path / Sheet URL / Sales Nav URL / paste manuale).
   ```

4. **Aspetta input lead** dall'utente

## Reconfigure trigger

User può dire (case-insensitive):

- "reconfigure" / "riconfigura"
- "voglio cambiare config" / "cambio configurazione"
- "ricomincia da capo" / "reset config"

→ Subagent:
1. Backup `<memory>/config.md` → `<memory>/config_backup_<timestamp>.md`
2. Ripete Q1-Q8 con default precedenti pre-popolati come hint
3. Salva nuovo config

## Edge case discovery

- Se utente skippa una Q (es. preme Esc o digita "skip"): default safe per quella Q (Founder, Hunter, Nessuno CRM, Manuale, ICP empty → ask follow-up, segmenti empty, 50-200 volume, SaaS 60/40 pattern)
- Se ICP description ambiguo (no geo, no industry): chiedi follow-up "Specifica almeno 1 industry e 1 geo"
- Se Q5 contains paese non-EU ma anche EU (es. "USA + Europa"): GDPR mode attivo solo per lead EU (filter geo)
