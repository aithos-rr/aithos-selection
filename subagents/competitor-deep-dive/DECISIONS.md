# DECISIONS — `/competitor-deep-dive`

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

## Decisioni iniziali (coordinator, 2026-04-30)

### [DECISION-001] Pattern Auto-Onboarding

**Contesto**: serve che ogni subagent diventi specifico per ruolo/settore/competitor utente.

**Decisione**: discovery interattiva al first run via AskUserQuestion (8 domande), salvataggio config in `<memory>/config.md`, re-prime config su run successivi.

**Alternative considerate**:
- Config tramite ENV vars → scartato: troppo developer-oriented per audience Learnn
- Config statica file pre-compilato → scartato: friction alta
- CLI flag → scartato: utente non ricorda flag

**Trade-off**: 2-3 min onboarding al first run, ma agent diventa "tuo".

**Reversibilità**: facile (cambia config.md o "reconfigure").

### [DECISION-002] Naming inglese kebab-case

**Contesto**: scelta lingua nomi subagent/skill.

**Decisione**: nomi tecnici inglese (kebab-case), messaggi utente italiano.

**Alternative considerate**:
- Tutto italiano → scartato: incoerente con ecosistema Anthropic
- Prefisso `/yt-` → scartato: meno pulito

**Trade-off**: nomi inglese da ricordare, ma sono standard.

### [DECISION-003] Riuso skill v1 trend-analysis come spunto (NON estensione)

**Contesto**: la skill v1 `webinar-2/trend-analysis` esiste e ha valore (analisi social trend). `/competitor-deep-dive` ne raddoppia lo scope ma con angolo diverso.

**Decisione**: spunto pattern (NotebookLM grounding, citazioni evidence-first, output markdown deterministico) ma il subagent v2 è **molto più ampio**: copre positioning + ToV + reviews G2/Trustpilot + tech stack BuiltWith + funding Crunchbase + gap matrix 6-dim. trend-analysis v1 resta in pack v1, non viene cancellata né ristrutturata.

**Alternative considerate**:
- Riscrivere zero ignorando v1 → scartato: butto via lavoro fatto
- Wrappare skill v1 dentro subagent → scartato: scope mismatch (trend-analysis è solo social, /competitor-deep-dive è multi-source enterprise-grade)

**Trade-off**: alcuni concept della skill v1 ricompaiono nel subagent (filosofia evidence-first). Coerenza brand.

### [DECISION-004] Memory scope = project

**Contesto**: dove salvare config persistente per `/competitor-deep-dive`.

**Decisione**: `memory: project` di default — i competitor analizzati sono per il progetto utente specifico (1 cliente = 1 lista competitor).

**Alternative considerate**:
- `memory: user` → utile se l'utente fa competitor analysis per più clienti diversi nello stesso settore. Ma normalmente la lista competitor cambia per cliente
- `memory: local` → solo locale al working dir, non sincronizzabile

**Trade-off**: scope project = config riusabile per re-run incrementali (re-fresh dossier ogni 90 giorni, aggiungere competitor). Cross-project bisogna ripetere discovery. Coverage migliore per use case tipico.

**Reversibilità**: facile (cambia frontmatter).
