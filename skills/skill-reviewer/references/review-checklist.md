# Skill Reviewer — Checklist 27 regole

## Contents

- [Frontmatter (12 regole)](#frontmatter-12-regole)
- [Struttura cartella (5 regole)](#struttura-cartella-5-regole)
- [Contenuto SKILL.md (7 regole)](#contenuto-skillmd-7-regole)
- [Pubblico business (3 regole)](#pubblico-business-3-regole-solo-se-audience-non-dev)
- [Pattern Claude 4.5/4.6-specific (3 regole)](#pattern-claude-4546-specific-3-regole)
- [Criteri di publish-ready](#criteri-di-publish-ready)
- [Comando audit one-liner](#comando-audit-one-liner)

## Frontmatter (12 regole)

### Obbligatori
1. **`name` presente, lowercase con trattini, ≤64 char**
   - 🟢 `name: lead-enrichment`
   - 🔴 `name: LeadEnrichment` / `Name: lead_enrichment`

2. **`description` presente, specifica cosa+quando**
   - 🟢 "Arricchisce lista lead con email verificata + LinkedIn. Usa quando hai CSV contatti grezzi."
   - 🔴 "Helper per lead"

3. **`description` + `when_to_use` combinati ≤1,536 char**
   - Usa `wc -c` per verificare
   - Se sfori, tronca `when_to_use` (è add-on, non essenziale)

### Raccomandati
4. **`description` front-loaded (critico nei primi 200 char)**
   - 🟢 "Genera briefing mattutino narrativo..." (subito claro)
   - 🔴 "Questa skill è pensata per chi vuole..." (wasting first line)

5. **`description` contiene ≥3 trigger phrases concrete**
   - 🟢 "Usa con backlog >20 email, rientro ferie, devo rispondere a molte email"
   - 🔴 "Usa quando serve" (zero trigger)

6. **`description` evita parole vaghe**
   - Banned: "cose", "helper", "tool per", "roba"
   - Ok: "classifica", "genera", "arricchisce", "audita"

7. **`argument-hint` se skill accetta argomenti**
   - 🟢 `argument-hint: "[folder-id]"`
   - 🔴 omesso ma `/skill <something>` previsto

8. **`allowed-tools` minimal (non `Bash` tout-court)**
   - 🟢 `allowed-tools: Read Grep Bash(git *)`
   - 🔴 `allowed-tools: Bash` (troppo permissivo)

9. **`disable-model-invocation: true` se side effect**
   - 🟢 skill deploy/commit/send con flag true
   - 🔴 skill `/deploy-prod` senza flag

### Opzionali ma utili
10. **`paths` glob se skill specifica per tipo file**
    - 🟢 skill per test Jest con `paths: "**/*.test.ts"`

11. **`model` / `effort` se task pesante o leggero**
    - 🟢 skill architecture con `effort: high`

12. **`context: fork` + `agent` se skill deve girare in subagent**
    - 🟢 skill research con `context: fork` e `agent: Explore`

## Struttura cartella (5 regole)

13. **SKILL.md < 500 righe**
    ```bash
    wc -l SKILL.md  # Deve essere <500
    ```
    - Se >500: sposta materiale in `references/` e linka

14. **No `README.md`/`CHANGELOG.md` nella cartella skill**
    - 🟢 solo file che AI usa
    - 🔴 README.md (quello sta a livello repo, non skill)

15. **Nomi file parlanti**
    - 🟢 `api-schema.json`, `frontmatter-fields.md`
    - 🔴 `data.json`, `stuff.md`

16. **`scripts/` hanno shebang se eseguibili**
    - 🟢 `#!/usr/bin/env python3` come prima riga
    - 🔴 script senza shebang, exec permission mancante

17. **`references/` sono linkati da SKILL.md**
    - 🟢 `[vedi references/xyz.md](references/xyz.md)` nel body
    - 🔴 file orfani, mai referenziati → morti in contesto

## Contenuto SKILL.md (7 regole)

18. **Struttura standard**
    ```
    # Titolo
    ## When to use
    ## Instructions
    ## Examples
    ## Gotchas
    ```

19. **"When to use" ha sia trigger sia anti-trigger**
    - 🟢 "Attiva se X, Y, Z. Non attivare se A, B"
    - 🔴 solo "Attiva quando serve"

20. **"Instructions" con step atomici, verbi imperativi**
    - 🟢 "1. Leggi file. 2. Parse JSON. 3. Scrivi output."
    - 🔴 "Questa skill può essere usata per..."

21. **"Examples" con ≥2 esempi concreti (input + output)**
    - 🟢 caso tipico + edge case
    - 🔴 nessun esempio

22. **"Gotchas" con errori REALI (non ipotetici)**
    - 🟢 "Token OAuth scade dopo 90gg inattività → re-run setup_oauth.py"
    - 🔴 "Potrebbe esserci un problema se..."

23. **Niente prima persona**
    - 🟢 "La skill legge Gmail e..."
    - 🔴 "Io leggo Gmail e..."

24. **Niente "Claudismi" (linguaggio robot, vaghezza)**
    - Banned: "I'll help you", "I can assist", "It depends"

## Pubblico business (3 regole, solo se audience non-dev)

25. **Zero jargon dev non spiegato**
    - 🟢 "estrazione dati" invece di "parsing"
    - 🔴 "endpoint REST" senza spiegazione

26. **Output orientato a risultato business**
    - 🟢 "Genera lista 50 lead pronti per outreach"
    - 🔴 "Esegue query SQL su database clienti"

27. **Istruzioni azionabili da chi capisce logica, non sintassi**
    - 🟢 steps in italiano business
    - 🔴 solo comandi shell criptici

## Pattern Claude 4.5/4.6-specific (3 regole)

Regole emerse dalla community ([ActiveMemory/ctx-skill-audit](https://github.com/ActiveMemory/ctx), [okwinds/skill-review-audit](https://github.com/okwinds/miscellany)) calibrate sui modelli Claude recenti, dove mandates rigidi e over-triggering hanno effetto peggiore che in passato.

28. **Positive framing**
    - 🟢 "Non fare X perché causa Y. Invece fai Z."
    - 🔴 "Non fare X." (senza counterpart)
    - Eccezione consentita nelle gotcha didattiche.

29. **Motivation over mandates**
    - 🟢 "Preferire A a B perché B introduce over-head di token senza migliorare output."
    - 🔴 "MUST NEVER use B. ALWAYS use A."
    - I modelli Claude 4.5/4.6 rispondono meglio al ragionamento che agli imperativi rigidi.

30. **Overtriggering calibration**
    - 🟢 description concise con 3-4 trigger specifici
    - 🔴 description piena di CAPS emphasis (CRITICAL, MUST, ALWAYS, NEVER) usati come enfasi
    - Eccesso di caps causa over-triggering indesiderato. Usare caps solo per acronimi (API, JSON, YAML).

## Criteri di publish-ready

- Zero blocker rosso + maggioranza verde: production-ready, pubblicabile
- 1-2 blocker rosso: applicare i fix prioritari in ordine, poi re-auditare
- 3+ blocker o fondamentali (description, gotchas, struttura) in rosso: major refactor o riscrittura con `/skill-builder`

## Comando audit one-liner

```bash
/skill-reviewer <path-skill-folder>
```

Report output nel formato:

```markdown
# Review /nome-skill
Path: <path>

## Blocker (rosso, N)
## Minor (giallo, N)
## OK (verde, N)

## Fix prioritari
1. ...
```
