# DECISIONS — `/web-builder`

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

**Contesto**: serve che ogni subagent diventi specifico per ruolo/stack/output utente.

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

### [DECISION-003] Default tech stack = `tech-stack-2026` di Filippo

**Contesto**: scelta del tech stack di default per un nuovo progetto web buildato dall'agent.

**Decisione**: baseline allineata a `~/.claude/skills/tech-stack-2026/SKILL.md` di Filippo: **Next.js 15 + Convex + Clerk + Tailwind v4 + shadcn/ui + Vercel**. Override permesso in Q3 della discovery.

**Alternative considerate**:
- Astro per landing → permesso come override (40-70% più performante per pure-static)
- Supabase invece di Convex → permesso come override (SQL-friendly per audience non-tech)
- una piattaforma no-code → permesso come override (no-code first)
- SvelteKit / Remix → scartato: meno community + meno tutorial 2026
- Stack agnostic con multi-template → scartato: friction alta, brand voice diluita

**Trade-off**: opinionato (forza scelte) ma allineato a expertise Filippo. L'utente può sempre override esplicito in Q3.

**Reversibilità**: facile (cambia in Q3 discovery o reconfigure).

### [DECISION-004] Memory scope = project

**Contesto**: dove salvare config persistente per `/web-builder`.

**Decisione**: `memory: project` di default — config legata al progetto web specifico (un repo = un progetto = un agent context).

**Alternative considerate**:
- `memory: user` → utile se l'utente builda decine di progetti con stesso stack. Ma normalmente ogni progetto ha tech stack/auth/DB diversi
- `memory: local` → solo locale al working dir, non persistente

**Trade-off**: scope project = config riusabile per build incrementali nello stesso progetto (auth setup, deploy, componenti aggiunti). Cross-project bisogna ripetere discovery. Coverage migliore.

**Reversibilità**: facile (cambia frontmatter).

## Decisioni emergent (worker chat, 2026-04-30 post-research Fase A)

### [DECISION-005] Astro override permesso per Q1=Landing

**Contesto**: `tech-stack-2026` di Filippo dice "Next.js sempre per web". Research RQ1 ha quantificato gap performance Astro vs Next.js per landing pure-static: Lighthouse 95-100 vs 80-85, payload <15KB vs 89KB, FCP <0.8s vs ~2.5s. Per landing/marketing/blog (alta priorità SEO/Core Web Vitals) il gap è non trascurabile.

**Decisione**: in discovery Q3, se Q1=Landing, proporre **Astro come default override** (con un warning: "Astro è 40-70% più performante per pure-static, ma se prevedi auth/DB poi serve migration"). Utente può ancora scegliere Next.js (es. se prevede di aggiungere SaaS funzionalità in futuro).

**Alternative considerate**:
- Forzare Next.js sempre → scartato: landing performance gap troppo grande, audience marketing-focused trarrebbe vantaggio
- Forzare Astro per Q1=Landing → scartato: utente potrebbe volere mix landing+auth (`(marketing)` route group in Next funziona)
- Lasciare scelta libera senza guidance → scartato: audience non-dev non sa decidere

**Trade-off**: agent ha logica condizionale (Q1+Q3 combination) ma utente ottiene tool right-sized. Riferimento da rispettare in skill `project-scaffolder` (template `astro-marketing` vs `nextjs-landing`).

**Reversibilità**: facile (utente cambia in Q3).

**Source research**: research-summary.md RQ1, [pkgpulse 2026 comparison](https://www.pkgpulse.com/guides/astro-vs-nextjs-2026), [DEV community 2026 framework guide](https://dev.to/pockit_tools/nextjs-vs-remix-vs-astro-vs-sveltekit-in-2026-the-definitive-framework-decision-guide-lp5).

### [DECISION-006] Convex confirmed default; Supabase permesso come override Q3

**Contesto**: BUILD-BRIEF chiede esplicito: "Filippo usa Convex (tech-stack-2026) ma molti tutorial citano Supabase — quando suggerire override?". Research RQ2 ha confermato: Convex è TypeScript-first (no SQL/migration learning curve), realtime built-in (sub-50ms latency), `npx convex dev` setup unico command. Supabase ha 50k MAU free tier vs Convex (più generoso) + RLS Postgres + open-source/self-hostable.

**Decisione**: Convex resta default (allineato `tech-stack-2026`). Override permesso in Q3 quando: (a) utente ha già DB Postgres legacy da connettere, (b) SQL knowledge esistente preferisce Postgres, (c) RLS multi-tenant pattern critico, (d) self-host requirement. Skill `auth-database-setup` ha branch `db_provider == 'supabase'`.

**Alternative considerate**:
- Forzare Convex sempre → scartato: utenti con SQL legacy bloccati
- Lasciare Supabase default → scartato: contraddice `tech-stack-2026`, audience non-dev preferisce concetti meno (no SQL/RLS)
- Multi-DB choice agnostic → scartato: friction alta, brand voice diluita

**Trade-off**: skill ha 2 branch (Convex/Supabase) raddoppiando complessità setup. Mitigato da reference docs separati (`database-integration-2026.md` con sezione Convex + sezione Supabase override).

**Reversibilità**: media (cambio post-build richiede migration manuale).

**Source research**: research-summary.md RQ2, [Convex vs Supabase 2026 — bertomill medium](https://bertomill.medium.com/convex-vs-supabase-which-backend-should-you-choose-in-2026-50d228c517de).

### [DECISION-007] Deploy automation OAuth-first via Vercel MCP, CLI fallback, token last resort

**Contesto**: BUILD-BRIEF flag "Deploy automation senza credenziali utente?". Research RQ8 ha confermato che **Vercel MCP esiste** a `https://mcp.vercel.com` (OAuth flow nativo, install via `claude mcp add --transport http vercel`), supporta Claude Code ufficialmente, ha confused-deputy protection. Token `VERCEL_TOKEN` resta supportato come fallback per CI o utenti advanced.

**Decisione**: Pattern detection a 3 livelli:
1. **Tier 1 — Vercel MCP available**: usa MCP per project create + env vars + deploy. OAuth handled da Claude Code (1 click browser), no token entry richiesto.
2. **Tier 2 — Vercel MCP non available, CLI installato**: ask user `vercel login` (browser OAuth one-time), poi tutte le operazioni via `vercel` CLI.
3. **Tier 3 — Token-only (CI / advanced)**: rispetta `VERCEL_TOKEN` env var esistente. Documenta come "advanced".

**Alternative considerate**:
- Solo CLI sempre → scartato: friction alta per audience non-dev, MCP riduce 1 step
- Solo MCP, no CLI fallback → scartato: MCP potrebbe non essere installato in tutti gli env
- Token-first → scartato: copia/incolla credenziali = anti-pattern security per non-dev

**Trade-off**: agent deve fare detection + branch logic. Mitigato da skill `deploy-automation` che incapsula complessità.

**Reversibilità**: facile (utente può sempre passare Tier 2 → Tier 3 manualmente).

**Source research**: research-summary.md RQ4 + RQ8, [vercel.com/docs/agent-resources/vercel-mcp](https://vercel.com/docs/agent-resources/vercel-mcp).

### [DECISION-008] Expo mobile template scope = STUB v1 + roadmap v2

**Contesto**: BUILD-BRIEF lista 5 template starter, incluso `expo-mobile/`. Research dice: audience Learnn (founder/marketer/freelancer non-dev) ha use case mobile <5%. Expo richiede setup aggiuntivo (Xcode/Android Studio per native build, simulator/device, app store account) che è friction-heavy per non-dev.

**Decisione**: in v1 dell'agent, includi `expo-mobile/` come **stub minimo** (`README.md` con "v2 scope" + link `tech-stack-2026` sez "Expo + Convex"). NON includere file Expo completi. Documenta come "Expo support coming v2 — per ora usa no-code platform/no-code per MVP mobile rapido".

**Alternative considerate**:
- Template Expo completo → scartato: 30+ file mobile, time-to-build doppio, audience minoritaria
- Skip Expo completamente → scartato: rompe coerenza con `tech-stack-2026` che lista Expo
- Solo placeholder vuoto → scartato: utente non capisce scope/roadmap

**Trade-off**: utenti mobile-first non hanno full support v1. Mitigato da: (a) audience minoritaria, (b) stub spiega scope chiaramente, (c) una piattaforma no-code funziona già per mobile MVP non-native.

**Reversibilità**: facile (v2 espande stub a template completo).

**Source research**: research-summary.md (audience analysis Learnn), `tech-stack-2026` skill globale (Expo è in stack ma marked "solo se serve native").
