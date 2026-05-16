# Schema Markup Guide 2026

> Reference doc per skill `schema-generator`. JSON-LD per page type, validation rules, gotcha critical (HowTo deprecated, FAQPage eligibility ristretta).

## JSON-LD = standard de-facto

[secondary, multi-source]:

> «JSON-LD is the dominant format in 2026, with Google explicitly recommending it»

Microdata e RDFa sono legacy. Per nuovo schema implementation, JSON-LD only.

## Schema injection pattern

```html
<head>
  <script type="application/ld+json">
  { ... JSON-LD here ... }
  </script>
</head>
```

CMS-specific:
- **WordPress**: Yoast SEO, Rank Math, Schema Pro plugins auto-inject
- **Next.js (app router)**: `metadata` API + manual `<Script>` JSON-LD
- **Astro**: `<Astro.Head>` slot + JSON-LD inline
- **Webflow**: custom code embed `<head>`
- **Shopify**: theme.liquid `<head>` + Liquid template per dynamic data

## Tier 1 schema types (priority 2026)

[secondary, [wpriders.com](https://wpriders.com/schema-markup-for-ai-search-types-that-get-you-cited/)]:

> «Tier 1 schema types (FAQPage, HowTo, Article, Organization) deliver the highest AI citation rates»

⚠ **Caveat HowTo + FAQPage** — vedi sezioni dedicate.

> «Pages with valid schema markup are 2-4x more likely to appear in Google's AI Overviews and featured snippets»

## Schema type completo

| Schema | Use case | 2026 status | Tier |
|--------|----------|-------------|------|
| `Article` | Blog post, news, guide | ✅ Active gold standard | Tier 1 |
| `Product` | E-commerce SKU | ✅ Active mandatory ecommerce | Tier 1 |
| `FAQPage` | Q&A page | ⚠ Eligibility ristretta gov/health (rich result) | Tier 1 LLM, Tier 2 Google |
| `Review` | Product review | ✅ Active (subject must exist) | Tier 2 |
| `AggregateRating` | Avg rating | ✅ Active (embed in Product/Service) | Tier 2 |
| `LocalBusiness` | Local SMB | ✅ Active mandatory local SEO | Tier 1 local |
| `Organization` | Company entity | ✅ Active sitewide head | Tier 1 |
| `BreadcrumbList` | Navigation | ✅ Active mandatory ecommerce | Tier 1 ecommerce |
| `Person` | Author bio | ✅ Active E-E-A-T signal | Tier 1 |
| `Event` | Event listing | ✅ Active | Tier 3 |
| `Course` | Online course | ✅ Active education | Tier 2 |
| `Recipe` | Recipe site | ✅ Active food | Tier 1 food |
| ~~`HowTo`~~ | Step-by-step | ❌ **Deprecated 2023** | Skip |

## Article — gold standard

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

Required:
- `headline` (≤110 char)
- `datePublished`
- `author` (Person with name, url, sameAs ideal)
- `publisher` (Organization with logo)
- `image` (1200px+ wide ideal)

## Product — ecommerce mandatory

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Scarpe Sneakers Modello X",
  "image": ["https://example.com/img/sku-x-1.jpg", "..."],
  "description": "...",
  "sku": "SKU-X-001",
  "brand": {"@type": "Brand", "name": "Brand Name"},
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product/sku-x",
    "priceCurrency": "EUR",
    "price": "89.90",
    "availability": "https://schema.org/InStock",
    "seller": {"@type": "Organization", "name": "..."}
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "127"
  }
}
```

## FAQPage — caveat critico

[primary, [Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/faqpage)]:

> «FAQ rich results are only available for well-known, authoritative websites that are government-focused or health-focused»

### Translation tattica

- **Eligible Google rich result**: gov, health, education_authority sites only
- **Schema utile ovunque**: per LLM citation (ChatGPT/Perplexity/Claude non hanno questa restrizione) — Tier 1 GEO

### DECISION-006 in `/seo-strategist`

Skill `schema-generator` propone FAQPage con warning trasparente se site_type ∉ {government, health, education_authority}:

> «Google rich result NON eligible per il tuo site type. Schema mantenuto per LLM citation (ChatGPT/Perplexity/Claude).»

### Required properties

- `mainEntity[]` of `Question` objects
- Each `Question`: `name` (full text question), `acceptedAnswer` (Answer object)
- Each `Answer`: `text` (full answer, può contenere HTML link/list)

### Constraint Google primary

- «Only use FAQPage if your page contains FAQs where there's a single answer to each question»
- Per multiple-answer (forum-style) → use `QAPage` instead
- «All FAQ content must be visible to the user on the source page»

### Esempio

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Cos'è il GEO?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "GEO è la pratica di ottimizzare content per essere citato da AI come ChatGPT, Perplexity, Claude."
      }
    }
  ]
}
```

## HowTo — deprecated

[secondary, multi-source]:

> «HowTo rich results were deprecated in 2023»

### Translation tattica

- Schema HowTo technically valido (non removed da Schema.org)
- MA: Google non genera rich result più
- Output: **MAI default** (DECISION-007 in `/seo-strategist`)

### Fallback: Article + nested ItemList

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Come configurare Google Analytics 4",
  "...": "...",
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Crea proprietà GA4", "url": "..."},
      {"@type": "ListItem", "position": 2, "name": "Installa script", "url": "..."}
    ]
  }
}
```

## LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "Restaurant",  // o sub-type LocalBusiness
  "name": "Trattoria Da Mario",
  "image": "...",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Via Roma 1",
    "addressLocality": "Bologna",
    "postalCode": "40100",
    "addressCountry": "IT"
  },
  "telephone": "+39-051-1234567",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "12:00",
      "closes": "23:00"
    }
  ],
  "priceRange": "€€",
  "servesCuisine": "Italian"
}
```

Required:
- `name`
- `address` (PostalAddress with streetAddress, addressLocality, postalCode, addressCountry)
- `telephone`
- `openingHoursSpecification`

## BreadcrumbList — ecommerce mandatory

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"},
    {"@type": "ListItem", "position": 2, "name": "Donna", "item": "https://example.com/donna"},
    {"@type": "ListItem", "position": 3, "name": "Scarpe", "item": "https://example.com/donna/scarpe"}
  ]
}
```

## Organization — sitewide head

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Yellow Tech",
  "url": "https://your-company.com",
  "logo": "https://your-company.com/logo.png",
  "sameAs": [
    "https://www.linkedin.com/company/your-company",
    "https://twitter.com/your-company"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+39-...",
    "contactType": "customer service",
    "areaServed": "IT",
    "availableLanguage": ["Italian", "English"]
  }
}
```

Best practice 2026: 1 Organization schema sitewide (homepage o footer-injected) + 1 schema specific per page.

## Validation

### Tier 1 (mandatory pre-deploy)

1. JSON syntax (Python `json.loads` o online JSON validator)
2. Schema.org property check (rule-based per type)
3. Required field presence

### Tier 2 (post-deploy)

1. [Schema.org Validator](https://validator.schema.org/) — manual test
2. [Google Rich Results Test](https://search.google.com/test/rich-results) — manual test, check eligibility
3. Search Console > Rich Results report (post-indexing)

### Anti-pattern

1. Schema content NOT visible on page (Google penalty risk)
2. Multiple `@type` conflitto (e.g., Article + Product on same `@id`)
3. Required field missing → no rich result
4. Invalid JSON syntax (silent fail)
5. Inflated rating (`AggregateRating` 4.9 con 1 review = unnatural pattern)

## Multiple schema same page (entity depth)

✅ ALLOWED, suggested 2026:

```
Article {
  author: Person { ... }
  publisher: Organization { ... }
  mainEntity: FAQPage { ... }
}
+
BreadcrumbList { ... }
```

Boost: entity depth signal per AI citation (Tier 1 GEO).

## Schema validation in CI/CD

Best practice 2026:

```bash
# Pre-commit hook
python3 scripts/schema_generator.py --validate --input schema-files/

# Schema-dts TypeScript type-check
npx tsc --noEmit
```

## Sources

### Primary

- [Schema.org](https://schema.org/) — full vocab
- [Google Search Central — structured data](https://developers.google.com/search/docs/appearance/structured-data)
- [Google Search Central — FAQPage](https://developers.google.com/search/docs/appearance/structured-data/faqpage)
- [Google Search Central — Article](https://developers.google.com/search/docs/appearance/structured-data/article)
- [Google Search Central — Product](https://developers.google.com/search/docs/appearance/structured-data/product)
- [Google Search Central — LocalBusiness](https://developers.google.com/search/docs/appearance/structured-data/local-business)

### Secondary

- [wpriders.com — schema for AI citation](https://wpriders.com/schema-markup-for-ai-search-types-that-get-you-cited/)
- [stackmatix.com — structured data AI search 2026](https://www.stackmatix.com/blog/structured-data-ai-search)
- [discoverability.co — schema markup guide 2026](https://discoverability.co/resources/schema-markup-guide/)
- [schema-dts](https://github.com/google/schema-dts) — TypeScript type-safe schema
