# GDPR Compliance — Lead Enrichment EU

> Reference per `/lead-finder-pro`. Auto-caricata se ICP description contains keyword EU/Europa/Italia/EMEA o paese EU (DECISION-011). Contiene LIA template editabile, 8-point checklist pre-outreach, sensitive data Article 9, opt-out workflow.

## Lawful basis: Legitimate Interest (Recital 47)

Recital 47 GDPR cita esplicitamente:

> "the processing of personal data for **direct marketing purposes** may be regarded as carried out for a legitimate interest"

Source: <https://gdpr-info.eu/recitals/no-47/>

### Le 3 condizioni del balancing test

Per usare legitimate interest come basis, devi dimostrare:

1. **Finalità legittima**: direct marketing B2B → fit naturale
2. **Necessità**: l'enrichment è necessario per raggiungere la finalità (sì se mirato, no se massivo non-targeted)
3. **Bilanciamento**: l'interesse del data controller NON deve overridare i fundamental rights del data subject

### "Reasonable expectations"

In B2B context, un professional in role specifico **può ragionevolmente aspettarsi** outreach business-relevant:

- ✅ VP Marketing in SaaS scaleup → ragionevole essere contattato per tool marketing
- ❌ Stessa persona contattata per offerte assicurative personali → fuori reasonable expectations

## LIA Template (Legitimate Interest Assessment)

Da copiare in `<memory>/lia_<segment>_<date>.md` per ogni segment ICP processato.

```markdown
# Legitimate Interest Assessment — <segment>

**Data**: YYYY-MM-DD
**Controller**: <nome utente / azienda>
**ICP target**: <descrizione>

## 1. Purpose test (legittima?)

- **Finalità**: direct marketing B2B verso <segment>
- **Beneficio per il controller**: pipeline qualificata, conversione a vendita
- **Beneficio per il data subject**: scoperta di soluzioni rilevanti per il suo ruolo

## 2. Necessity test (necessaria?)

- **Alternativa considerata**: paid ads, content marketing inbound
- **Perché enrichment è necessario**: targeting preciso evita spam massivo, riduce contact rate non-rilevante, rispetta meglio il time del prospect

## 3. Balancing test (proporzionata?)

- **Dati raccolti**: solo professionali (job title, company, email business, linkedin)
- **Dati esclusi (Article 9)**: ❌ health, ❌ origine etnica/razziale, ❌ opinioni politiche, ❌ credenze religiose, ❌ home address, ❌ social non-business
- **Reasonable expectation**: VP Marketing/Founder/SDR in <segment> si aspetta outreach business
- **Opt-out garantito**: link unsubscribe in OGNI email, processato entro 24h, score -25 in CRM

## Outcome: legitimate interest VALID per <segment>

**Firma**: <nome utente>
**Review schedulato**: ogni 6 mesi
```

## 8-point checklist pre-outreach

Da eseguire (subagent automatica) prima di consegnare lista finale Hot leads:

1. ✅ **LIA documentato** per il segment processato (file `lia_*.md` esiste)
2. ✅ **Privacy Policy** linkabile (controller ha pagina pubblica con dettaglio enrichment + retention)
3. ✅ **Source documented**: ogni lead ha `_source` field (Hunter, Apollo, LinkedIn URL, etc.)
4. ✅ **No Article 9 sensitive data** nello schema (validation script reject)
5. ✅ **Data minimization rispettato**: solo professional fields (`name, company, role, email, linkedin, industry, size`)
6. ✅ **Opt-out infrastructure pronto**: link unsubscribe, processing entro 24h
7. ✅ **Retention policy chiara**: lead non convertiti dopo 12 mesi → flag review
8. ✅ **Negative scoring active**: -25 unsubscribe, -40 competitor, applied automatically

Output report `gdpr_check_<timestamp>.md` con esito 8/8 pass o lista issue.

## Sensitive data — Article 9 (NON arricchire)

Special categories vietate per direct marketing:

- 🚫 Razza / origine etnica
- 🚫 Opinioni politiche
- 🚫 Credenze religiose / filosofiche
- 🚫 Appartenenza sindacale
- 🚫 Dati biometrici / genetici
- 🚫 Dati salute / vita sessuale / orientamento

**Schema validation in `/lead-finder-pro`**: se input CSV contiene una di queste field (e.g. `religion`, `political_party`, `health_condition`) → schema reject + error message all'utente.

### Esclusi anche per "reasonable expectation"

- 🚫 Home address (se non business address pubblico)
- 🚫 Personal phone (non-business)
- 🚫 Private social media activity (Instagram personale, TikTok)
- 🚫 Family / relationship status

## Opt-out handling workflow

### Hunter Error 451 mechanism

Hunter signals via Error 451 quando un individual ha richiesto "do not process my personal data" — questo lead è automaticamente excluso da future enrichment via Hunter.

`/lead-finder-pro` skill `email-verification`:

```text
if hunter_response.status_code == 451:
    mark_lead(lead, status='opted_out', exclude_future=True)
    skip_outreach(lead)
    log_to_compliance_register(lead, action='opt_out_hunter_451', timestamp=now())
```

### Unsubscribe handling

Quando lead unsubscribe via email outbound:

1. **Immediate cessation**: rimuovi da TUTTE le active sequence entro 24h
2. **Apply negative signal**: -25 punti score (skill `icp-scoring`)
3. **Suppression list**: aggiungi a `<memory>/suppression_list.md` per evitare re-enrichment futuro
4. **Audit log**: entry in `compliance_register_<year>.md` con timestamp + lead email

### Subject Access Request (SAR)

Se un lead richiede "voglio sapere cosa avete su di me":

1. Cerca lead in tutti i CSV/Sheet/Attio CRM (skill query_all_lead_sources)
2. Compila report con: dati raccolti, source, retention policy, processing purpose
3. Consegna entro 30 giorni (deadline GDPR)
4. Se richiede deletion → execute deletion + add a suppression list

## Retention policy guidance

| Lead status | Retention max | Trigger review |
|-------------|---------------|----------------|
| Hot (Grade A) attivo | 24 mesi | Job-change alert (re-evaluate) |
| Warm (B) | 12 mesi | No activity 6 mesi → review |
| Cold (C) | 6 mesi | Auto-delete dopo 6 mesi se zero touch |
| Disqualified / Opted-out | indefinito (suppression only) | Conservato in suppression list per evitare re-contact |

## EU country detection

Lista paesi EU + EFTA per auto-detection in ICP description:

```text
EU 27: Austria, Belgium, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia,
Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania,
Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia,
Spain, Sweden

EFTA (GDPR-aligned): Iceland, Liechtenstein, Norway, Switzerland (with SCC)

UK: post-Brexit, ICO ha proprio regime ma allineato; trattare come GDPR-equivalent
```

Italian keyword variants:

```text
"Italia", "Italy", "italiana", "italiano"
"Europa", "Europe", "europea", "europeo"
"EMEA", "EU", "Unione Europea"
```

## Workflow pratico SDR/BDR/Founder per stay compliant

### Setup once (5 min)

1. Compila LIA per ogni segment ICP target → salva in `<memory>/lia_*.md`
2. Verifica Privacy Policy presente sul sito (link pubblico)
3. Setup unsubscribe link in tutti i template outbound
4. Configura suppression list `<memory>/suppression_list.md`

### Per ogni nuova lista lead (run `/lead-finder-pro`)

1. Subagent rileva EU → auto-load `gdpr-compliance.md` + warning utente
2. Subagent applica 8-point checklist + validation Article 9
3. Output report `gdpr_check_<timestamp>.md` con esito
4. Se issue → blocco output finché user fixa

### Periodicamente (mensile)

- Review LIA: ancora valida? Segment cambiato?
- Audit suppression list: dimensione coerente con outreach volume?
- Compliance register: tutti opt-out tracciati?

## Disclaimer legale

Questa reference è **guida operativa**, non parere legale. Per implementazione production: consulta DPO o legal counsel certificato GDPR. Filippo Greco / `/lead-finder-pro` non assume responsabilità per uso non-compliant.

Source primaria: <https://gdpr-info.eu/recitals/no-47/> + best practice Hunter, Amplemarket, IntentDepth (2026 reviews).
