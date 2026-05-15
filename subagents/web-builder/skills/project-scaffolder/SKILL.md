---
name: project-scaffolder
description: Genera la struttura cartelle e i file base di un progetto web partendo da un template starter. Sostituisce placeholder come {{PROJECT_NAME}}, {{AUTHOR}}, {{DOMAIN}} con i valori reali, esegue init git, e fa npm install. Da usare in Phase 2 della methodology /web-builder, dopo che la discovery ha determinato template_id e config. Audience non-developer Learnn.
when_to_use: Phase 2 di /web-builder, scaffold iniziale Next.js/Astro/Expo project, copia template + placeholder substitution, init git
---

# Project Scaffolder

Skill di Phase 2 della methodology `/web-builder`. Prende un `template_id` e una config discovery, e produce un progetto reale on disk con git inizializzato e dipendenze installate.

## When to use

Attiva quando:
- L'utente ha completato discovery (Q1-Q8) e c'è `<memory>/config.md` valido
- `config.build.scaffold_done` è `false`
- `config.project.path` non esiste o è vuoto

**Non attivare se**:
- Discovery incompleta (manca config)
- Path già scaffoldato (`config.build.scaffold_done == true`) — usa altre skill per modifiche incrementali
- Path esistente con file (handle edge case prima — vedi sez "Edge cases")

## Input contract

```yaml
template_id: nextjs-saas | nextjs-landing | astro-marketing | next-internal-tool | expo-mobile | no-code-only
project_name: my-saas              # kebab-case, da config.project.name
project_path: /path/to/project     # da config.project.path
options:
  author: "Filippo Greco"          # opzionale, da CLAUDE.md root
  domain: "my-saas.com"            # opzionale, da config.project.domain
  description: "SaaS per X"        # opzionale, da Q1+Q3 narrative
  auth_provider: clerk             # da config.stack.auth
  db_provider: convex              # da config.stack.database
  payments: stripe | autumn | none # da config.stack.payments
```

## Output contract

```yaml
status: success | partial | failed
path: /path/to/project
files_created:
  - package.json
  - app/layout.tsx
  - app/page.tsx
  - convex/schema.ts
  - .gitignore
  - CLAUDE.md (placeholder, viene compilato in Phase 3)
  - ...
files_skipped:                     # se merge mode con cartella esistente
  - existing-file.md
git_initialized: true
npm_install_completed: true
warnings:
  - "Node v18 detected, recommend v20+"
next_steps:
  - "Compile CLAUDE.md (Phase 3)"
  - "Setup auth + DB (Phase 4)"
```

## Workflow

### Step 1 — Validate template

1. Read `scripts/templates/<template_id>/` directory
2. Verifica esistenza file critici: `package.json`, `tsconfig.json` (se Next/Expo), `astro.config.mjs` (se Astro)
3. Se template missing → fail con error message "Template <id> non trovato in scripts/templates/. Disponibili: nextjs-saas, nextjs-landing, astro-marketing, next-internal-tool, expo-mobile"

### Step 2 — Validate destination path

1. Check `os.path.exists(project_path)`
2. Se non esiste → crea via `os.makedirs(project_path)` e procedi
3. Se esiste e vuoto → procedi
4. Se esiste con file → **edge case** (vedi sez "Edge cases handling")

### Step 3 — Copy template + placeholder substitution

```bash
# Pseudocode (impl reale in scripts/scaffold_project.py)
cp -r scripts/templates/<template_id>/* <project_path>/
cd <project_path>
find . -type f \( -name "*.json" -o -name "*.tsx" -o -name "*.ts" -o -name "*.md" -o -name "*.astro" -o -name "*.mjs" -o -name "*.config.*" \) | xargs sed -i.bak 's/{{PROJECT_NAME}}/<project_name>/g'
find . -name "*.bak" -delete
# Repeat per {{AUTHOR}}, {{DOMAIN}}, {{DESCRIPTION}}
```

Placeholder lista (in ordine di priorità):

| Placeholder | Valore source |
|---|---|
| `{{PROJECT_NAME}}` | `project_name` (es. `my-saas`) |
| `{{PROJECT_NAME_TITLE}}` | Title case (es. `My Saas`) |
| `{{AUTHOR}}` | `options.author` o `"You"` default |
| `{{DOMAIN}}` | `options.domain` o `"<project>.vercel.app"` default |
| `{{DESCRIPTION}}` | `options.description` o `"<project_name> built with /web-builder"` default |
| `{{YEAR}}` | Anno corrente (es. `2026`) |

### Step 4 — Init git

```bash
cd <project_path>
git init
git branch -M main
git add .gitignore  # primo file added (NO add -A)
git add package.json README.md CLAUDE.md  # file core
git add app/ src/ public/ convex/ lib/    # cartelle code (se esistono)
git add tsconfig.json next.config.* astro.config.* tailwind.config.*  # config
git commit -m "Initial scaffold via /web-builder — <stack>"
```

**Anti-pattern**: `git add -A` o `git add .` (rischio committare `.env.local` se utente l'ha già creato manualmente).

### Step 5 — npm install

```bash
cd <project_path>
node --version  # check v20+
npm install
```

Edge: se `npm install` fail con peer dep conflict, retry con `npm install --legacy-peer-deps` (1x retry max). Se fail di nuovo, abort + report log all'utente.

### Step 6 — Output user

```
✅ Scaffold completato in `<project_path>` (<N> file creati)

📂 Struttura principale:
  app/                  # Next.js App Router
  ├── layout.tsx        # Root layout
  ├── page.tsx          # Home
  └── (dashboard)/      # Protected routes
  components/           # React components (vuoto, popolato Phase 5)
  convex/               # Backend Convex (vuoto, popolato Phase 4)
  lib/                  # Utilities
  public/               # Static assets
  CLAUDE.md             # Placeholder, compilo in Phase 3
  package.json
  .env.local.example    # Da compilare in Phase 4

🚀 Test locale: cd <project_path> && npm run dev (http://localhost:3000)

Procedo con CLAUDE.md preconfigurato? [Sì/No]
```

## Edge cases handling

### Cartella esistente con file

Se `os.listdir(project_path)` non vuoto e cartella non è solo `.git/`:

```
⚠️  Trovo file esistenti in `<path>`:
   - file1.md
   - file2.tsx
   ... (N totali)

Cosa vuoi fare?
1. **Merge**: scaffold sopra esistenti, prompt per ogni conflitto
2. **Backup**: rinomina esistenti in `<path>.bak/` poi scaffold pulito
3. **Abort**: annulla, scegli altro path

Scegli [1/2/3]:
```

MAI overwrite silenzioso. MAI `rm -rf` senza autorizzazione.

### Node version mismatch

```bash
node --version
# v18.x.x → warning
```

Se v<20 e Q2 != "senior":
```
⚠️  Node v18 rilevato, consigliato v20+ per Next.js 15.

Procedo lo stesso? [Sì/Aggiorna Node prima]
  → Aggiorna: `nvm install 20 && nvm use 20`
```

Se Q2=senior, skip warning + procedi.

### Template missing

Se `scripts/templates/<template_id>/` non esiste:
```
❌ Template `<id>` non trovato.

Disponibili in v1:
  - nextjs-saas (default per SaaS micro)
  - nextjs-landing (Next.js per landing con Convex)
  - astro-marketing (Astro per landing/content)
  - next-internal-tool (variant nextjs-saas senza billing)
  - expo-mobile (stub v1, v2 scope)

Vuoi cambiare scelta? [reconfigure / abort]
```

### no-code platform-only mode (Q3=no-code platform)

Skip frontend scaffold:
1. Crea solo struttura cartelle: `backend/n8n-workflows/`, `data/`, `docs/`, `.claude/`
2. Genera CLAUDE.md placeholder (Phase 3 lo compila)
3. Genera `docs/no-code-prompt.md` template (riusa pattern `vibe-start` skill v1)
4. Skip Phase 4 (no-code platform handles auth+DB)
5. Output user: instructions per setup una piattaforma no-code manuale

## Examples

### Esempio A — SaaS micro standard

```
Input:
  template_id: nextjs-saas
  project_name: freelance-crm
  project_path: ~/Dev/projects/freelance-crm
  options: {auth_provider: clerk, db_provider: convex, payments: stripe}

Output: ~30 file scaffolded, git init, npm install ok, dev server ready
Time: ~3-5 min (mostly npm install)
```

### Esempio B — Astro landing minimal

```
Input:
  template_id: astro-marketing
  project_name: ai-mastery-2026
  project_path: ~/Dev/projects/ai-mastery-2026
  options: {auth_provider: none, db_provider: none, domain: "ai-mastery.com"}

Output: ~15 file scaffolded (no auth/DB), Tailwind v4 + shadcn, content collections, Lighthouse 95+
Time: ~2-3 min
```

## Gotchas

- 🔴 **Placeholder substitution con `sed`**: macOS `sed -i` richiede arg vuoto (`sed -i ''`), Linux no. Lo script Python `scaffold_project.py` gestisce diff platform.
- 🔴 **Hidden files**: `cp -r` di default non copia file con `.` iniziale (`.gitignore`, `.env.example`). Use `cp -rT` o list explicit.
- 🟡 **Naming case-sensitive**: macOS HFS+ è case-insensitive di default → `MyComponent.tsx` e `mycomponent.tsx` collidono. Force lowercase su filenames generati.
- 🟢 **Lazy install**: skip `npm install` se Q2=senior (utente fa lui), risparmiamo 2-3 min.

## References

- `references/stack-comparison-2026.md` — decision matrix template
- `scripts/templates/<template_id>/` — file sorgenti template
- `scripts/scaffold_project.py` — wrapper Python con error handling

## Crediti

Skill creata per `/web-builder` (Pack v2 Learnn). Pattern derivato da `vibe-start` skill v1 (Webinar 3 Vibe Coding).
