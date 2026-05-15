---
name: sequence-builder
description: Genera sequence JSON portable da template (A/B/C/D) + value prop + brand voice + signal leads. Multi-channel email + LinkedIn timing widening gap (DECISION-010). A/B test branching subject + first-line. GDPR footer enforcement bilingue. Output schema portable per upload SmartLead/HeyReach. Per `/outbound-orchestrator` skill core methodology Fase 4.
when_to_use: Build sequence per nuova campagna outbound, custom template definition, A/B test variant generation, re-build sequence dopo signal update, audit sequence pre-execute
---

# Sequence Builder

Genera sequence JSON portable (DECISION-015 schema) per upload SmartLead/HeyReach. Combina template + leads enriched + first-line variants + GDPR footer in output single file.

**Lingua**: italiano user-facing, inglese tecnico (sequence_name, step_n, channel, ecc.).

## When to use

Attiva quando:
- Build sequence per nuova campagna (Fase 4 metodologia `/outbound-orchestrator`)
- Custom template definition (utente vuole template non standard A/B/C/D)
- Re-build sequence post signal update (ri-personalize per signal nuovi)
- Audit sequence pre-execute (sample 10 lead)
- A/B test new variant testing

**Non attivare** se:
- Lead non personalizzati (chain `personalization-engine` mancante)
- Template non selezionato (config `sequence.template` empty)
- GDPR footer non disponibile (chain `gdpr-opt-out` mancante per EU)

## Prerequisites

- Lead enriched + personalized JSON (output `personalization-engine`)
- Config `<memory>/config.md` con `sequence.template`, `sequence.default_length`, `sequence.multi_channel`, `sequence.ab_test_enabled`
- GDPR footer HTML (chain `gdpr-opt-out` se `gdpr.mode_active`)
- Reference `references/sequence-templates.md` per 4 template structure
- Reference `references/api-recipes.md` per HeyReach single-brace + SmartLead double-brace differenze

## Inputs

```json
{
  "leads_personalized": [
    {
      "lead_id": "uuid",
      "first_name": "Marco",
      "last_name": "Rossi",
      "email": "marco.rossi@company.com",
      "company": "Acme",
      "linkedin_url": "https://linkedin.com/in/marco-rossi",
      "role": "CMO",
      "industry": "SaaS B2B",
      "first_line_variants": [
        {"variant": "A", "text": "Ciao Marco, vidi che..."},
        {"variant": "B", "text": "Ciao Marco, complimenti..."},
        {"variant": "C", "text": "Ciao Marco, il salto..."}
      ],
      "signal_used": "job_change"
    }
  ],
  "config": {
    "campaign_name": "Yellow Tech — Series A SaaS Q2 2026",
    "template": "direct_demo",
    "sequence_length": 5,
    "multi_channel": true,
    "ab_test": true,
    "brand_voice": "direct",
    "value_prop": "GTM Engineering audit gratuito per SaaS B2B post-Series A",
    "signature": "Filippo Greco — Yellow Tech",
    "gdpr_footer_html": "<p>...</p>"
  }
}
```

## Outputs

`output/sequence_<campaign_name_kebab>_<ts>.json`:

```json
{
  "campaign_name": "Yellow Tech — Series A SaaS Q2 2026",
  "campaign_name_kebab": "yellow-tech-series-a-saas-q2-2026",
  "sequence_name": "direct_demo_5step_v1",
  "template_used": "direct_demo",
  "channels": ["email", "linkedin"],
  "ab_test": true,
  "steps": [
    {
      "step_n": 1,
      "channel": "email",
      "delay_days": 0,
      "send_window": "tue_thu_9_13",
      "subject_variants": ["Domanda su {company}", "{first_name}, {company} + GTM"],
      "body_variants": ["Ciao {first_name},\n\n{first_line_variant_a}\n\n...", "Ciao {first_name},\n\n{first_line_variant_b}\n\n..."],
      "signal_used_template": "job_change",
      "stop_conditions": ["reply", "bounce", "unsubscribe"]
    },
    {
      "step_n": 2,
      "channel": "linkedin",
      "node_type": "CONNECTION_REQUEST",
      "delay_days": 2,
      "messages": ["Ciao {first_name}, ho visto..."],
      "fallback_message": "Ciao {first_name}, mi piacerebbe connetterci."
    },
    {
      "step_n": 3,
      "channel": "email",
      "delay_days": 5,
      "subject_variants": ["Re: ..."],
      "body_variants": ["..."]
    },
    {
      "step_n": 4,
      "channel": "linkedin",
      "node_type": "MESSAGE",
      "delay_days": 7,
      "messages": ["Grazie per la conn! Volevo..."],
      "conditional": "is_connection_accepted"
    },
    {
      "step_n": 5,
      "channel": "email",
      "delay_days": 10,
      "subject_variants": ["Ultimo: {company} GTM"],
      "body_variants": ["Ciao {first_name},\n\nIn 2 righe..."]
    }
  ],
  "leads": [
    {
      "lead_id": "uuid",
      "email": "marco.rossi@company.com",
      "first_name": "Marco",
      "last_name": "Rossi",
      "company": "Acme",
      "linkedin_url": "https://linkedin.com/in/marco-rossi",
      "custom_fields": {
        "first_line_a": "Ciao Marco, vidi che sei passato a CMO ad Acme...",
        "first_line_b": "Ciao Marco, complimenti per il nuovo ruolo...",
        "first_line_c": "Ciao Marco, il salto da VP Marketing...",
        "li_message1": "Ciao Marco, ho visto del nuovo ruolo a Acme — congrats!",
        "li_message2": "Grazie per la conn! Volevo chiederti...",
        "signal_used": "job_change"
      }
    }
  ],
  "gdpr_footer_html": "<p>...</p>",
  "lia_doc_path": "<memory>/lia_yellow_tech_series_a_saas_q2_2026.md",
  "_meta": {
    "created_at": "2026-04-30T11:30:00Z",
    "agent": "outbound-orchestrator",
    "schema_version": 1,
    "config_snapshot": { ... }
  }
}
```

## Methodology

### 1. Template selection

```python
TEMPLATES = {
    "direct_demo": load_template("direct_demo_5step.json"),
    "education_first": load_template("education_first_7step.json"),
    "pain_discovery": load_template("pain_discovery_5step.json"),
    "multi_threading": load_template("multi_threading_5step.json"),
    "custom": None
}

template = TEMPLATES[config["template"]]
if template is None:
    template = build_custom_template(config["custom_steps"])
```

### 2. Apply widening gap timing (DECISION-010)

Default gap matrix per email step:

```python
WIDENING_GAP = {
    1: 0,       # step 1: day 0
    2: 2,       # step 2: day 2 (LinkedIn) or +5 if email-only
    3: 5,       # step 3: day 5
    4: 7,       # step 4: day 7 (LinkedIn) or +10 if email-only
    5: 10,      # step 5: day 10
    6: 14,      # step 6: day 14 (break-up)
    7: 21       # step 7: day 21 (final break-up enterprise)
}
```

Multi-channel offset:

```python
MULTI_CHANNEL_OFFSET = {
    "email_to_linkedin": 2,   # email day 0 → LinkedIn day 2
    "linkedin_to_msg": 5      # connect day 2 → message day 7 (post-acceptance)
}
```

### 3. A/B test branching

Se `config.ab_test = true`:

```python
def generate_ab_variants(step_template, voice, value_prop):
    """Generate 2 subject + 2 body variants per step."""
    subject_variants = generate_subject_pair(step_template, voice)
    body_variants = generate_body_pair(step_template, voice, value_prop)
    return {
        "subject_variants": subject_variants,
        "body_variants": body_variants
    }
```

LLM call per generate variant pairs. Store both, SmartLead `is_split_test: true` activates 50/50 distribution.

### 4. Personalization injection

Per ogni lead, inject `first_line_variants` nel body template via placeholder `{first_line_variant_a}`, `{first_line_variant_b}`, `{first_line_variant_c}`:

```python
def inject_first_lines(body_template, lead_first_lines):
    """Replace {first_line_variant_X} placeholders with lead-specific text."""
    body = body_template
    for variant in lead_first_lines:
        placeholder = f"{{first_line_variant_{variant['variant'].lower()}}}"
        body = body.replace(placeholder, variant["text"])
    return body
```

NOTA: per SmartLead use double-brace `{{first_name}}`, per HeyReach use single-brace `{first_name}`. Skill `sequence-builder` produce schema portable single-brace, conversion fatta in `smartlead_upload.py` (per email body) o `heyreach_upload.py` (per LinkedIn body) prima di API call.

### 5. LinkedIn step generation

```python
def build_linkedin_steps(template, leads):
    """Generate LinkedIn steps with HeyReach single-brace placeholder."""
    steps = []

    # Step Connection Request (if multi-channel)
    if template["multi_channel"]:
        steps.append({
            "step_n": 2,
            "channel": "linkedin",
            "node_type": "CONNECTION_REQUEST",
            "delay_days": 2,
            "messages": [
                f"Ciao {{first_name}}, ho visto del {{signal_phrase}} — mi piacerebbe connetterci."
            ],
            "fallback_message": "Ciao {first_name}, mi piacerebbe connetterci."
        })

    # Step Message (post-acceptance)
    if template["sequence_length"] >= 5:
        steps.append({
            "step_n": 4,
            "channel": "linkedin",
            "node_type": "MESSAGE",
            "delay_days": 7,
            "messages": [
                "Grazie per la conn! Volevo continuare la conversazione..."
            ],
            "conditional": "is_connection_accepted"
        })

    return steps
```

### 6. GDPR footer enforce

Se `gdpr.mode_active = true`, inject `{footer_html}` placeholder in ogni email body:

```python
def enforce_gdpr_footer(body, footer_html):
    """Append footer if not already present."""
    if "{footer_html}" not in body and "{{footer_html}}" not in body:
        body = body.rstrip() + "\n\n{footer_html}"
    return body.replace("{footer_html}", footer_html)
```

NOTA: skill `gdpr-opt-out` produce footer bilingue se EU detected.

### 7. Stop conditions

Default per ogni step:

```python
STOP_CONDITIONS = ["reply", "bounce", "unsubscribe"]
```

Se reply detected → pause sequence (managed by SmartLead webhook → `reply-classification`).
Se bounce → suppress immediato.
Se unsubscribe → suppress cross-stack.

### 8. Sample preview (audit pre-execute)

```python
def generate_sample_preview(sequence, leads, n=3):
    """Generate human-readable preview for 3 random leads."""
    sample = random.sample(leads, min(n, len(leads)))
    preview = []
    for lead in sample:
        preview.append({
            "lead_email": lead["email"],
            "rendered_steps": [
                render_step(step, lead) for step in sequence["steps"]
            ]
        })
    return preview
```

Output preview Markdown:

```markdown
## Sample preview — Lead 1: marco.rossi@company.com

**Step 1 (Email, day 0)**:
Subject: Domanda su Acme

Ciao Marco,

Ciao Marco, vidi che sei passato a CMO ad Acme a marzo. Congrats!

Lavoriamo con SaaS Series A su scaling GTM dopo round. Ti sembrerebbe utile vedere come?

Filippo Greco — Yellow Tech

[Footer GDPR bilingue, opt-out link]

**Step 2 (LinkedIn, day 2)**:
Connection request + nota: "Ciao Marco, ho visto del nuovo ruolo a Acme — congrats! Mi piacerebbe connetterci."

...
```

User reviews preview before "execute" command.

## Examples

### Example 1 — Direct Demo 5-step multi-channel A/B test on

**Input**: 50 lead grade A, template `direct_demo`, multi-channel, A/B test on, voice direct.

**Output**: sequence JSON con:
- 5 steps (email day 0, LinkedIn day 2, email day 5, LinkedIn day 7, email day 10)
- 2 subject variants per email step
- 2 body variants per email step (using A/B first-line)
- LinkedIn single-brace placeholder
- GDPR footer bilingue
- 50 leads with `first_line_a`, `first_line_b`, `first_line_c` custom fields

### Example 2 — Education-First 7-step email-only enterprise

**Input**: 20 lead enterprise CMO, template `education_first`, email-only, A/B test off, voice educational.

**Output**: sequence JSON con:
- 7 email steps (day 0, 5, 7, 14, 21, 30, 45)
- 1 subject + 1 body per step
- Insight-first content (no pitch fino a step 5)
- Resource downloads embedded
- Long-cycle break-up

### Example 3 — Pain Discovery 5-step pain-first

**Input**: 30 lead, template `pain_discovery`, voice friendly.

**Output**: sequence JSON con:
- Step 1 = domanda diagnostica (NO pitch)
- Step 2 condizionale: se reply → branch positivo; se no reply → standard sequence
- Step 3-5 standard

NOTA: branching condizionale gestito a livello SmartLead campaign settings (sub-sequences), NON in JSON portable.

## Anti-pattern

1. **Mai sequence senza widening gap** (daily bump = ban risk Gmail trasformer)
2. **Mai mix single-brace/double-brace** in stesso template (vendor differences gestite at upload time)
3. **Mai skip GDPR footer enforcement** se EU detected
4. **Mai genera sequence senza first-line variants** (chain `personalization-engine` mandatory)
5. **Mai >7 step** in singola sequence (ROI decay, fatigue lead)
6. **Mai LinkedIn message senza CONNECTION_REQUEST** prima (HeyReach API constraint, conditional `is_connection_accepted`)
7. **Mai duplicate sequence variants identical** (anti-LLM-detection check)
8. **Mai assume timezone unica** (multi-geo lead → per-lead timezone scheduling)

## Scripts

- `../../scripts/sequence_build.py` — CLI wrapper (consumed da subagent main)
- Embedded in `smartlead_upload.py` + `heyreach_upload.py` (parse sequence JSON, translate per vendor)

## References

- `../../references/sequence-templates.md` — 4 template structure A/B/C/D + JSON examples
- `../../references/prompt-patterns.md` — first-line variant generation
- `../../references/api-recipes.md` — vendor-specific syntax differences

## Output destination

`output/sequence_<campaign_name_kebab>_<ts>.json` (portable schema)
+ optional `output/sequence_preview_<ts>.md` (human review)
