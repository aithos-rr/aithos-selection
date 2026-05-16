# DECISIONS — `/lead-finder-pro`

> Append-only log di decisioni importanti (architectural, scope, trade-off). Immutable per default — non riscrivere, solo aggiungere.

## Format entry

```markdown
## YYYY-MM-DD HH:MM — [DECISION-N] Titolo decisione

**Contesto**: cosa stavamo affrontando
**Decisione**: cosa abbiamo scelto
**Alternative considerate**: cosa abbiamo scartato e perché
**Trade-off**: pro e contro
**Reversibilità**: facile/media/difficile
```

## Decisioni iniziali (coordinator, 2026-04-29)

### [DECISION-001] Pattern Auto-Onboarding

**Contesto**: serve che ogni subagent diventi specifico per ruolo/stack/ICP utente.

**Decisione**: discovery interattiva al first run via AskUserQuestion (6-8 domande), salvataggio config in `<memory>/config.md`, re-prime config su run successivi.

**Alternative considerate**:
- Config tramite ENV vars → scartato: troppo developer-oriented per audience Learnn
- Config statica file pre-compilato → scartato: utente deve studiare frontmatter, friction alta
- Config via CLI flag → scartato: utente non ricorda flag

**Trade-off**: 2 min di onboarding al first run, ma agent diventa "tuo" — vale la pena.

**Reversibilità**: facile (cambia config.md per testare).

### [DECISION-002] Naming inglese

**Contesto**: scelta lingua nomi subagent/skill.

**Decisione**: nomi tecnici inglese (kebab-case), messaggi utente italiano.

**Alternative considerate**:
- Tutto italiano → scartato: incoerente con ecosistema Anthropic
- Prefisso /yt- → scartato: meno pulito, conflitti potenziali

**Trade-off**: nomi inglese richiedono che utente li ricordi, ma sono standard.

### [DECISION-003] Riuso skill v1 come spunto

**Contesto**: 4 skill W2 esistenti (lead-enrichment, ecc.) hanno valore.

**Decisione**: spunto + ispirazione, MA il subagent v2 va molto più in profondità (300-500 righe vs 170). Skill v1 restano disponibili in pack v1, non vengono cancellate.

**Alternative considerate**:
- Riscrivere zero ignorando v1 → scartato: butto via lavoro fatto
- Wrappare skill v1 dentro subagent → scartato: duplicazione, manutenzione doppia

**Trade-off**: alcuni concept della skill v1 saranno duplicati nel subagent (filosofia, gotchas).

### [DECISION-004] Memory scope = project

**Contesto**: dove salvare config persistente.

**Decisione**: `memory: project` di default per `/lead-finder-pro` (config per progetto utente).

**Alternative considerate**:
- `memory: user` → utile se l'utente fa lead gen per più clienti diversi nello stesso ICP. Ma normalmente ICP cambia per progetto.
- `memory: local` → solo locale al working dir, non sincronizzabile

**Trade-off**: se l'utente ha 1 progetto solo, project = user. Se ha multi-progetto, project = ICP per progetto. Coverage migliore.

**Reversibilità**: facile (cambia frontmatter).

## Decisioni emergent da Fase A research (worker chat, 2026-04-29 19:20)

### [DECISION-005] Hunter MCP come primary email finder/verifier

**Contesto**: Q2 research ha rivelato che Hunter è l'unico provider top-10 con MCP server nativo (`mcp.hunter.io`), permettendo natural-language interaction da Claude. Apollo ha solo REST API; ZoomInfo enterprise; Cognism EU-only.

**Decisione**: chain default email enrichment = **Hunter MCP → Apollo API fallback → manual SMTP last resort**. Skill `email-verification` e `waterfall-enrichment` codificano questa priorità.

**Alternative considerate**:

- Apollo first (più economico, $49/mese vs Hunter premium) → scartato: bounce 15-25% Apollo richiede comunque verification esterna, e Hunter MCP riduce friction significativamente
- Clay first (orchestrator multi-provider) → scartato: $185/mese tier minimo, costi credit imprevedibili, non MCP-native
- Cognism first → scartato: EU-only, coverage drop fuori EU

**Trade-off**: Hunter premium tier può costare > Apollo per high-volume; ma per audience Learnn (founder/SDR/marketer freelance, low-volume tipico <200 lead/mese) Hunter MCP free tier + premium opzionale è il path più semplice.

**Reversibilità**: facile (utente in discovery può scegliere altro tool primary, fallback chain è configurabile in `config.md`).

### [DECISION-006] Skills weighting fit/behavior 60/40 default

**Contesto**: Q3 research ha consolidato split 60/40 fit/behavior come default 2026 SaaS sales-led. NotebookLM ha fornito tabella numerica completa.

**Decisione**: skill `icp-scoring` espone 3 template con default 60/40 (SaaS B2B sales-led) + variant 50/50 (Agency, dove relationship signal pesa più) + variant 70/30 (eCommerce, dove fit firmografico domina). Soglie grade band fisse: A 90-100, B 75-89, C 50-74, Disqualified <50.

**Alternative considerate**:

- Single template hard-coded → scartato: audience eterogenea (SaaS, Agency, eCommerce, Founder freelance)
- Fully configurabile via discovery → scartato: friction alta per non-tech, 8 domande discovery sono già il limite

**Trade-off**: 3 template coprono ~80% audience, ma utente edge case (es. enterprise B2B large) può dover personalizzare via `references/icp-scoring-framework.md`.

**Reversibilità**: facile (template Markdown editabile).

### [DECISION-007] Signal decay 50%/mese applicato di default

**Contesto**: Q3 research → behavioral signals decadono e devono essere ricalcolati. 50%/mese è citato come consolidato 2026.

**Decisione**: skill `icp-scoring` applica signal decay 50%/mese sui punti behavioral; field `enriched_at` timestamp obbligatorio nel JSON intermedio per calcolo decay.

**Alternative considerate**:

- No decay (score statico) → scartato: leads vecchi con score alto sono misleading
- Decay più aggressivo 70%/mese → scartato: troppo conservativo, taglia troppo segnale valido
- Decay configurabile per signal type → utile ma over-engineering per v1; introducibile in v2 se serve

**Trade-off**: 50% può essere troppo o troppo poco per business specifico; documentato in references `icp-scoring-framework.md` come tunable.

**Reversibilità**: facile (parametro `signal_decay_monthly: 0.5` in config).

### [DECISION-008] Coverage threshold waterfall = 85% match rate

**Contesto**: Q1, Q4 research → 85% email match rate è la soglia consolidata 2026 prima di considerare "complete" un waterfall enrichment.

**Decisione**: skill `waterfall-enrichment` break al primo match verified e somma vendor finché 85% coverage raggiunta su batch (default 100 lead). Sotto 85%, log warning + suggerisci aggiungere vendor extra.

**Alternative considerate**:

- 75% (più leggero) → scartato: sotto consolidato 2026
- 90% (Q1 menziona "≥90%") → scartato: troppo aggressivo per audience entry-level Learnn (tier free/basic, vendor disponibili limitati)

**Trade-off**: 85% è middle ground; utenti enterprise possono alzare a 90%+ via config.

**Reversibilità**: facile.

### [DECISION-009] Conflict-resolution policy = flag, not auto-pick

**Contesto**: Edge case da Fase A: provider diversi possono restituire valori diversi (es. Hunter vs Apollo email diverse per stesso prospect). Auto-pick first è rischioso (qualità non uguale tra provider).

**Decisione**: skill `waterfall-enrichment` flagga il conflict in field `_conflicts: [{field, providers, values}]` e marca lead come "needs_review" se conflict critico (email, phone). User può definire policy custom in config (`conflict_policy: flag | auto_first | auto_highest_confidence`).

**Alternative considerate**:

- Auto-pick first sempre → scartato: degrada qualità silently
- Auto-pick highest confidence → richiede normalizzazione confidence cross-provider, non triviale per v1

**Trade-off**: aggiunge step manual review per ~5-10% lead (in esperienza tipica), ma evita CRM pollution.

**Reversibilità**: facile (policy config).

### [DECISION-010] Manual-field protection mandatory

**Contesto**: Q1 research → "human-in-the-loop accuracy" deve essere protetta da automated overwrite.

**Decisione**: schema config supporta `manual_fields_protected: [email, phone, role]` (default lista con questi 3); skill `waterfall-enrichment` write-only-to-empty-fields su questi campi, MAI overwrite. Altri campi possono essere overwriten.

**Alternative considerate**:

- Always overwrite (semplice) → scartato: rischio distruzione lavoro manuale
- Sempre flag never overwrite (zero auto) → scartato: friction alta, audience non-tech non vuole troppi prompt

**Reversibilità**: facile.

### [DECISION-011] EU auto-load GDPR reference

**Contesto**: Q5 research → GDPR è una compliance area critica con specifici requirement; audience Learnn ha base utenti EU significativa (Filippo stesso EU-based).

**Decisione**: il subagent al first run dopo discovery, **se ICP description contains "EU", "Europa", "Italia", "EMEA", o lista geo include paesi EU**, auto-carica `references/gdpr-compliance.md` come priority context e mostra warning "Modalità GDPR attiva: LIA richiesto, opt-out enforcement, dati sensibili filtrati".

**Alternative considerate**:

- Sempre attivo GDPR mode → scartato: overhead non necessario per US-only campaigns
- Solo on-explicit-request → scartato: rischio compliance per chi dimentica

**Reversibilità**: facile (logic in system prompt + skill `gdpr-compliance` logic).

### [DECISION-012] Sonnet model (not Opus) per agent

**Contesto**: BUILD-BRIEF suggerisce `model: sonnet` come default. Research non ha cambiato il quadro.

**Decisione**: confermato `model: sonnet` per `/lead-finder-pro`. Cost-effective per audience Learnn, capable enough per task structured (waterfall enrichment, scoring, GDPR check). Opus rimane opzione opt-in via config.

**Alternative considerate**:

- Opus default → scartato: cost ~5x, audience freelance/SDR sensibile al pricing
- Haiku → scartato: troppo limitato per discovery + multi-step methodology

**Reversibilità**: facile (frontmatter `model` field).
