---
name: schema-generator
description: Genera Schema.org JSON-LD per page type (Article, Product, FAQPage, Review, LocalBusiness, Organization, BreadcrumbList, AggregateRating, Person/Author). Validation pre-deploy mandatory via Schema.org validator + Google Rich Results Test. Anti-pattern enforcement — HowTo MAI default (deprecated 2023), FAQPage con warning eligibility (Google rich result solo gov/health, schema utile per LLM citation per altri site type). Output JSON-LD pronto per `<head>` injection in CMS template.
when_to_use: Schema markup generation per nuovo content piece, fix schema invalid esistente, batch schema rebuild post audit, schema injection in CMS template (WordPress, Webflow, Shopify, Next.js, Astro)
---

# Schema Generator

Skill che produce schema markup JSON-LD validated, anti-pattern-aware, gold-standard 2026.

## Scope

- **In scope**: JSON-LD generation per 9 schema type principali, validation pre-deploy, gotcha enforcement (HowTo deprecated, FAQPage eligibility)
- **Out of scope**: schema injection automatic in CMS (output JSON-LD ready, deployment manuale o via CMS plugin)

## Schema type supportati

| Schema | Use case | 2026 status | Priority Tier |
|--------|----------|-------------|---------------|
| `Article` | Blog post, news, guide | ✅ Active, gold standard | Tier 1 |
| `Product` | E-commerce SKU | ✅ Active, mandatory ecommerce | Tier 1 |
| `FAQPage` | Q&A page | ⚠ Eligibility ristretta gov/health (Google rich result), utile per LLM citation | Tier 1 LLM, Tier 2 Google |
| `Review` | Product review | ✅ Active (subject must exist) | Tier 2 |
| `AggregateRating` | Avg rating display | ✅ Active, embed in Product/Service | Tier 2 |
| `LocalBusiness` | Local SMB | ✅ Active, mandatory local SEO | Tier 1 local |
| `Organization` | Company entity | ✅ Active, sitewide head | Tier 1 |
| `BreadcrumbList` | Navigation breadcrumb | ✅ Active, ecommerce mandatory | Tier 1 ecommerce |
| `Person` | Author bio | ✅ Active, E-E-A-T signal | Tier 1 |
| ~~`HowTo`~~ | Step-by-step guide | ❌ **Deprecated 2023** — fallback Article + nested ItemList | Skip |
| `Event` | Event listing | ✅ Active | Tier 3 |
| `Course` | Online course | ✅ Active, education site | Tier 2 education |
| `Recipe` | Recipe site | ✅ Active, food site | Tier 1 food |

## Input contract

```yaml
schema_type: Article | Product | FAQPage | Review | LocalBusiness | Organization | BreadcrumbList | Person | Event | Course | Recipe
page_url: https://example.com/blog/...
page_metadata:
  title: "..."
  description: "..."
  date_published: 2026-05-01
  date_modified: 2026-05-01
  author_name: "Mario Rossi"
  author_url: optional
  author_same_as: [optional list of social URL]
  publisher_name: "..."
  publisher_logo_url: "..."
  image_url: "..."
content_extract: optional  # for FAQPage Q&A extraction
site_type: saas_b2b | ecommerce | content_blog | local | agency  # da Q3 discovery, governs eligibility warnings
```

## Methodology

### Step 1 — Type validation

1. Check schema_type ∈ supported list
2. **HowTo guard**: se schema_type=HowTo → reject + warning «HowTo deprecated 2023. Fallback Article + nested ItemList preserved better.» (DECISION-007)
3. **FAQPage guard**: se schema_type=FAQPage AND site_type ∉ {government, health, education_authority} → output schema MA con warning trasparente:

```text
⚠ FAQPage schema generato MA Google rich result NON eligible per il tuo site type ({site_type}).
Schema mantenuto per LLM citation (ChatGPT/Perplexity/Claude) — pattern Tier 1 GEO.
Source: https://developers.google.com/search/docs/appearance/structured-data/faqpage
```

### Step 2 — Required field check

Per ogni schema type, validate required field presence:

| Schema | Required fields |
|--------|-----------------|
| `Article` | headline, datePublished, author, publisher, image |
| `Product` | name, image, description, offers (price + availability + priceCurrency) |
| `FAQPage` | mainEntity[] of Question (each with name + acceptedAnswer.text) |
| `LocalBusiness` | name, address (PostalAddress), telephone, openingHoursSpecification |
| `Organization` | name, url, logo |
| `BreadcrumbList` | itemListElement[] with position + item.name + item.@id |
| `Person` | name, url (optional but recommended for E-E-A-T) |

Se field missing → reject + list missing fields.

### Step 3 — JSON-LD generation

Output JSON-LD pronto per `<script type="application/ld+json">` injection.

Esempio Article (gold standard 2026):

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Ecommerce Analytics Guide 2026",
  "image": "https://example.com/img/cover.jpg",
  "datePublished": "2026-05-01T08:00:00+02:00",
  "dateModified": "2026-05-01T08:00:00+02:00",
  "author": {
    "@type": "Person",
    "name": "Mario Rossi",
    "url": "https://example.com/author/filippo-greco",
    "sameAs": [
      "https://www.linkedin.com/in/filippogreco/",
      "https://twitter.com/filippogreco"
    ]
  },
  "publisher": {
    "@type": "Organization",
    "name": "Yellow Tech",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/blog/ecommerce-analytics-guide-2026"
  }
}
```

### Step 4 — Validation

Validation tier 1 (mandatory pre-output):
1. JSON syntax validation (Python `json.loads`)
2. Schema.org property validation against type spec (rule-based per supported types)
3. Required field presence (re-check)

Validation tier 2 (suggested post-output):
1. [Schema.org Validator](https://validator.schema.org/) — manual user check
2. [Google Rich Results Test](https://search.google.com/test/rich-results) — manual user check

Output flag: `validated_tier1: true` + suggestion to user run tier 2.

### Step 5 — Anti-pattern detection

Pre-output, check anti-pattern:
- `Article` no `dateModified` → warning
- `Product` no `priceCurrency` o `availability` → reject
- `LocalBusiness` no `address` o `telephone` → reject
- `Author` no `sameAs` → suggestion (E-E-A-T weak signal)
- Multiple schema same page (es. Article + FAQPage + BreadcrumbList) → ALLOWED, suggested actually (entity depth)

## Output JSON schema

```json
{
  "schema_type": "Article",
  "page_url": "https://example.com/blog/...",
  "generated_at": "2026-05-01T16:30:00Z",
  "json_ld": { ... full JSON-LD ... },
  "validation": {
    "tier1_syntax": "pass",
    "tier1_required_fields": "pass",
    "tier1_property_check": "pass",
    "warnings": [
      "FAQPage rich result not eligible for site_type=saas_b2b"
    ]
  },
  "anti_pattern_flags": [],
  "deployment_instructions": {
    "html_injection": "<script type=\"application/ld+json\">...</script>",
    "wp_plugin_compatible": ["Yoast SEO", "Rank Math", "Schema Pro"],
    "next_js": "import inside <Head> component or app router metadata API"
  }
}
```

## Anti-hallucination contract

- Mai inventare URL placeholder (`example.com/...`) se user non fornisce — chiedi user value
- Mai output schema con required field mancante senza reject
- Mai output HowTo schema (DECISION-007)
- FAQPage warning sempre presente se site_type non eligible
- Validation tier1 mandatory pre-output

## Edge cases

1. **Multiple authors** → array author[] con multiple Person object
2. **Multilingual page (hreflang)** → 1 schema per lingua, distinct URL per lingua
3. **Variant Product** (size, color) → main Product + Offer[] varianti
4. **AggregateRating no review** → reject (rating senza review = manipulative signal)
5. **Event past date** → flag + suggest update to next occurrence
6. **Recipe schema** Italian recipe site → ensure `recipeCuisine: "italian"` + `inLanguage: "it"`

## Tool integration

| Tool | Use | Cost |
|------|-----|------|
| Schema.org Validator | Validation web | Free |
| Google Rich Results Test | Validation web | Free |
| Yoast SEO (WordPress) | Auto-injection | Free + Premium |
| Rank Math (WordPress) | Auto-injection | Free + PRO |
| Schema Pro (WordPress) | Auto-injection | $79/yr |
| `schema-dts` (TypeScript) | Type-safe schema in Next.js | Free OSS |

## CLI invocation

```bash
python3 scripts/schema_generator.py \
  --type Article \
  --url https://example.com/blog/topic \
  --metadata page-meta.yaml \
  --site-type saas_b2b \
  --validate \
  --output output/schema-article.json
```

## Output downstream

JSON-LD → consumed da:
- Main agent Fase 5 (technical fix + schema injection)
- CMS template (manual user injection o via plugin)
- `/document-factory` (PDF schema markup audit report)

## References

- `references/schema-markup-guide-2026.md` — full schema type guide + gotcha
- `references/seo-best-practices-2026.md` — E-E-A-T schema signals (Author + Organization)

## Examples

### Example 1: Article schema

Input: schema_type=Article, page metadata complete, site_type=content_blog.

Output: JSON-LD Article + Person Author with sameAs LinkedIn/Twitter + Organization Publisher with logo. Validation tier1 pass. No warnings.

### Example 2: FAQPage schema saas_b2b

Input: schema_type=FAQPage, site_type=saas_b2b, content_extract with 6 Q&A.

Output: JSON-LD FAQPage + warning trasparente «Google rich result NON eligible per saas_b2b. Schema mantenuto per LLM citation (Tier 1 GEO).» Validation tier1 pass.

### Example 3: HowTo guard

Input: schema_type=HowTo, site_type=content_blog.

Output: REJECTED + warning «HowTo schema rich result deprecated 2023 (Google). Suggerisco fallback Article + nested ItemList per preserve structured data without rich result expectation.» + esempio Article+ItemList incluso.
