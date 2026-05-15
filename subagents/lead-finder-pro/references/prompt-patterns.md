# Prompt Patterns — `/lead-finder-pro`

> Reference per il modello del subagent quando l'utente chiede aiuti specifici (es. "scrivimi messaggio per VP marketing SaaS Hot lead", "draft outreach per cold lead Director eCom"). Pattern + template + esempi.

## Quando l'utente chiede prompt assistance

L'utente potrebbe dire (case-insensitive):

- "scrivimi un messaggio per [lead name / segment]"
- "draft email outreach per [segment]"
- "personalizza per [Hot/Warm] [grade]"
- "fammi opener per LinkedIn DM [role]"
- "subject line A/B test per [campaign]"

→ Il subagent attiva sezione "Prompt Assistance" (Methodology Fase 5 opzionale post-output).

## Pattern 1 — Hot lead VP/Director outreach (cold email)

**Input requirement** (dal subagent ha già):

- `name`, `company`, `role`, `industry`, `score_breakdown` (perché Hot)
- `intent_signals` (cosa li rende Hot adesso)

**Template**:

```text
Subject: <hook 4-7 parole referenziando intent signal>

Ciao <FirstName>,

<Apertura referenziando 1 fatto specifico — funding, hiring, role recente, news>.

<Bridge: collegamento al pain del segment / problema risolto dal product>.

<CTA soft: domanda specifica vs demo richiesta. Es. "Hai 15 min mar pomeriggio per capire come [outcome specifico]?">

<Firma + 1 line value prop / signature breve>
```

### Esempio output (dato come few-shot al modello)

Input:

- name: Sara Bianchi
- role: VP Marketing
- company: Nimbus FinTech (50-200 employees, Italy)
- industry: FinTech B2B SaaS
- score: 92 (Hot A)
- intent_signals: ["Series A €15M Feb 2026", "hiring 3 marketing roles"]

Output:

```text
Subject: post-Series A: marketing stack scaling questions

Ciao Sara,

ho visto il post di funding di Nimbus a febbraio e i 3 ruoli marketing aperti —
sembra il momento in cui le cose esplodono o si rompono.

Lavoriamo con altri founder marketing FinTech post-Series A che gestiscono il
salto da 5 a 15 lead/giorno senza far esplodere il CAC. Senza vendere niente:
in 15 minuti ti mostro cosa fanno quelli che riescono e dove inciampano.

Hai mar 12/3 o gio 14/3 pomeriggio?

Filippo
GTM Engineer @ Yellow Tech
PS: se mar/gio non funzionano, dimmi quando — niente automated calendar.
```

## Pattern 2 — Warm lead Director (multi-touch nurture sequence)

**Input requirement**:

- `name`, `company`, `role`, score 75-89 (B grade)
- Indicatore di "warmness" (newsletter subscriber, content download, partial demo)

**Template** (sequence 3-5 touch):

### Touch 1 — Reference content che hanno consumato

```text
Subject: <riferimento al content scaricato> + question

Ciao <FirstName>,

ho visto che hai scaricato [content piece]. La domanda che mi viene è:
[domanda contestuale al loro role + content].

Il motivo: <1 bullet personalizzato sul segment>.

Curioso di sapere come la vivete in [Company]. 1 frase ti basta.

Filippo
```

### Touch 2 (5 giorni dopo) — Insight specifico

```text
Subject: [Insight specifico segment]

Ciao <FirstName>,

[Insight crudo, dato concreto]: <es. "Le agency post-Series A hanno tipicamente
14 mesi di runway prima del prossimo round; il 70% di quelle che bruciano CAC
nei primi 6 mesi non arriva al next round.">

Significa che [implication per il loro role].

Se è rilevante, posso mostrartelo in pratica con [tool / case study]. 15 min.

Filippo
```

### Touch 3 (10 giorni dopo) — CTA finale

```text
Subject: ultima ping — vale la pena?

<FirstName>,

ti ho scritto 2 volte. O sono fuori target o il timing è sbagliato.

Se è il primo, dimmi "non rilevante" e mi tolgo dalle scatole.
Se è il secondo, dimmi quando torna utile e mi rifaccio vivo.

Filippo
```

## Pattern 3 — LinkedIn DM opener (warm intro)

**Constraint**: max 300 char, no link (LinkedIn flag), tono diretto.

**Template**:

```text
Ciao <FirstName>, ho visto [trigger specifico - post recente / role nuovo / connection
mutual]. <1 frase: cosa noti / domanda]. Non vendo niente, sono curioso di [insight
specifico]. Tempo 5 min su quel tema?
```

### Esempio

Input: Mario Rossi, post LinkedIn su "ABM is dead"

Output:

```text
Ciao Mario, ho visto il tuo post sul perché ABM tradizionale ha smesso di funzionare.
Curioso: lo vedi confermato anche nei segment outbound o solo inbound? Sto trovando
pattern diversi per founder vs Director e mi piacerebbe capire la tua. 5 min in DM?
```

## Pattern 4 — Subject line A/B variants

Quando user chiede "draftami 3 subject line per [campaign]":

**Pattern formati 2026 che funzionano**:

1. **Question hook**: "<role>, ti capita che <pain>?"
2. **Number/specificity**: "<X>% di <segment> <achievement> in <timeframe>"
3. **Curiosity gap**: "[Brand competitor] vs [loro stack]: il dato strano"
4. **Direct ask**: "15 min mar 12 alle 14 — discovery <topic>?"
5. **Insight tease**: "Quello che <segment leader> non dice su <topic>"
6. **Reference name**: "<Mutual contact> mi ha menzionato te"
7. **Provocazione utile**: "Smetti di fare <common mistake>?"

**Anti-pattern da evitare** (2026 spam filter trigger):

- 🚫 "Quick question" / "Quick chat" (over-used)
- 🚫 "Re: <fake reply>" se non c'è thread reale
- 🚫 ALL CAPS o emoji nel subject
- 🚫 "<FirstName>" senza personalization reale dopo
- 🚫 "5x growth in 30 days" (claim non-verificabili)

## Pattern 5 — Personalization sweet spot

**Formula** (dal training data 2026 outbound):

> Personalization line = (1 fact specifico + 1 implication + 1 hook value prop) in ≤2 frasi.

**Esempi**:

✅ Buono: "Ho visto che Acme ha aperto 3 ruoli SDR negli ultimi 30 giorni.
Tipicamente significa che il volume outbound sta scalando ma il process non è ancora
sistematizzato. Ti mostro cosa fanno gli altri prima di assumere il 4°?"

❌ Bad (generico): "Ho visto che lavori in marketing presso Acme. Volevo presentarti
il nostro tool che aiuta marketing manager a fare di più con meno."

❌ Bad (creepy): "Ho visto che hai scaricato [content X], visitato [page Y] 3 volte,
e che il tuo CFO è Mario Rossi. Volevo proporti..."

## Pattern 6 — GDPR-safe outbound EU

Quando lead EU + GDPR mode attivo, ogni email outbound deve includere:

1. **Source disclosure** in firma o footer (1 riga): "Ho il tuo contatto via [Hunter / LinkedIn / Apollo]; non vuoi più ricevere mie email? <unsubscribe link>"
2. **Unsubscribe link** funzionante (test ogni mese)
3. **Privacy Policy link** in firma
4. **No tracker pixel** invasivo (basic open tracking ok se documentato in Privacy Policy)

### Esempio firma GDPR-safe

```text
--
Filippo Greco | GTM Engineer @ Yellow Tech
filippo@yourdomain.it | linkedin.com/in/yourname

Source: ho trovato il tuo contatto via [Hunter/LinkedIn].
Privacy: yourdomain.it/privacy | Unsubscribe: <link>
```

## Pattern 7 — Output prompt per il subagent stesso

Quando user chiede al subagent "spiegami perché questo lead è Hot":

**Template risposta**:

```text
**<Lead Name>** — Score <X>, Grade <Y>

Punti forti (perché Hot):
- <signal 1>: +<X> punti (categoria)
- <signal 2>: +<X> punti
- <signal 3>: +<X> punti

Punti di attenzione:
- <signal con score basso o conflict, se presente>

Recommendation:
- <action concreta: outreach immediato? sequence specifica? warm intro?>

Source enrichment:
- <Hunter / Apollo / LinkedIn / etc.>

Confidence: <high / medium / low> (basata su email_confidence + role_confidence)
```

## Anti-pattern prompt assistance

L'agent NON deve mai:

- 🚫 Inventare fatti specifici sul lead se non in `_enriched` data
- 🚫 Generare subject line con claim numerici non-verificabili ("5x growth")
- 🚫 Scrivere DM/email senza esplicito opt-in dell'utente per il send
- 🚫 Saltare GDPR check su lead EU prima di draft outbound
- 🚫 Suggerire mass-personalization (centinaia di varianti uguali)
- 🚫 Auto-send: il draft va sempre proposto all'utente per review

## Cross-reference

- Skill `icp-scoring` espone `score_breakdown` → input per Pattern 7 explanation
- Skill `gdpr-compliance` valida outbound EU → input per Pattern 6
- Subagent Methodology Fase 5 (output) → output del subagent diventa input per prompt assistance
