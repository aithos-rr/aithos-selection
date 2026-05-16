#!/usr/bin/env python3
"""schema_generator.py — Genera Schema.org JSON-LD per page type.

Tipi supportati: Article, Product, FAQPage, LocalBusiness, Organization, BreadcrumbList, Person, Review.
Validation tier 1 (syntax + required field) mandatory.
HowTo guard: reject + suggest fallback Article+ItemList.
FAQPage guard: warning se site_type non-eligible Google rich result.

Usage:
    python3 schema_generator.py --type Article --metadata page-meta.yaml --site-type saas_b2b --validate
    python3 schema_generator.py --type FAQPage --metadata faq.yaml --site-type content_blog --output schema.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({"error": "PyYAML missing: pip install -r requirements.txt"}))
    sys.exit(1)


SUPPORTED_TYPES = {
    "Article",
    "Product",
    "FAQPage",
    "LocalBusiness",
    "Organization",
    "BreadcrumbList",
    "Person",
    "Review",
    "AggregateRating",
}

DEPRECATED_TYPES = {"HowTo"}

FAQPAGE_ELIGIBLE_SITE_TYPES = {"government", "health", "education_authority"}

REQUIRED_FIELDS = {
    "Article": ["headline", "datePublished", "author", "publisher"],
    "Product": ["name", "image", "offers"],
    "FAQPage": ["mainEntity"],
    "LocalBusiness": ["name", "address", "telephone"],
    "Organization": ["name", "url"],
    "BreadcrumbList": ["itemListElement"],
    "Person": ["name"],
    "Review": ["reviewRating", "author", "itemReviewed"],
    "AggregateRating": ["ratingValue", "reviewCount"],
}


def load_metadata(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        if path.endswith(".yaml") or path.endswith(".yml"):
            return yaml.safe_load(f) or {}
        return json.load(f)


def build_article(meta: dict) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta.get("title", "")[:110],
        "datePublished": meta.get("date_published"),
        "dateModified": meta.get("date_modified") or meta.get("date_published"),
    }
    if meta.get("image_url"):
        schema["image"] = meta["image_url"]
    if meta.get("author_name"):
        author = {
            "@type": "Person",
            "name": meta["author_name"],
        }
        if meta.get("author_url"):
            author["url"] = meta["author_url"]
        if meta.get("author_same_as"):
            author["sameAs"] = (
                meta["author_same_as"]
                if isinstance(meta["author_same_as"], list)
                else [meta["author_same_as"]]
            )
        schema["author"] = author
    if meta.get("publisher_name"):
        publisher = {
            "@type": "Organization",
            "name": meta["publisher_name"],
        }
        if meta.get("publisher_logo_url"):
            publisher["logo"] = {
                "@type": "ImageObject",
                "url": meta["publisher_logo_url"],
            }
        schema["publisher"] = publisher
    if meta.get("page_url"):
        schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": meta["page_url"]}
    return schema


def build_product(meta: dict) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": meta.get("name", ""),
        "image": meta.get("image_url") or meta.get("images", []),
    }
    if meta.get("description"):
        schema["description"] = meta["description"]
    if meta.get("sku"):
        schema["sku"] = meta["sku"]
    if meta.get("brand_name"):
        schema["brand"] = {"@type": "Brand", "name": meta["brand_name"]}
    if meta.get("price") and meta.get("currency"):
        schema["offers"] = {
            "@type": "Offer",
            "url": meta.get("page_url", ""),
            "priceCurrency": meta["currency"],
            "price": str(meta["price"]),
            "availability": meta.get("availability", "https://schema.org/InStock"),
        }
    if meta.get("rating_value") and meta.get("review_count"):
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(meta["rating_value"]),
            "reviewCount": str(meta["review_count"]),
        }
    return schema


def build_faqpage(meta: dict) -> dict:
    questions = meta.get("questions", [])
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": q.get("answer", ""),
                },
            }
            for q in questions
        ],
    }
    return schema


def build_localbusiness(meta: dict) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": meta.get("business_type", "LocalBusiness"),
        "name": meta.get("name", ""),
    }
    if meta.get("image_url"):
        schema["image"] = meta["image_url"]
    if meta.get("address"):
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": meta["address"].get("street", ""),
            "addressLocality": meta["address"].get("city", ""),
            "postalCode": meta["address"].get("postal_code", ""),
            "addressCountry": meta["address"].get("country", "IT"),
        }
    if meta.get("telephone"):
        schema["telephone"] = meta["telephone"]
    if meta.get("opening_hours"):
        schema["openingHoursSpecification"] = meta["opening_hours"]
    if meta.get("price_range"):
        schema["priceRange"] = meta["price_range"]
    return schema


def build_organization(meta: dict) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": meta.get("name", ""),
        "url": meta.get("url", ""),
    }
    if meta.get("logo_url"):
        schema["logo"] = meta["logo_url"]
    if meta.get("same_as"):
        schema["sameAs"] = meta["same_as"]
    return schema


def build_breadcrumb(meta: dict) -> dict:
    items = meta.get("items", [])
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": item.get("name", ""),
                "item": item.get("url", ""),
            }
            for i, item in enumerate(items)
        ],
    }


def build_person(meta: dict) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": meta.get("name", ""),
    }
    if meta.get("url"):
        schema["url"] = meta["url"]
    if meta.get("same_as"):
        schema["sameAs"] = meta["same_as"]
    if meta.get("job_title"):
        schema["jobTitle"] = meta["job_title"]
    if meta.get("works_for"):
        schema["worksFor"] = {"@type": "Organization", "name": meta["works_for"]}
    return schema


BUILDERS = {
    "Article": build_article,
    "Product": build_product,
    "FAQPage": build_faqpage,
    "LocalBusiness": build_localbusiness,
    "Organization": build_organization,
    "BreadcrumbList": build_breadcrumb,
    "Person": build_person,
}


def validate_schema(schema: dict, schema_type: str) -> dict:
    """Tier 1 validation: syntax + required field check."""
    issues = []

    # Syntax check (already JSON dict)
    if not isinstance(schema, dict):
        return {"valid": False, "issues": ["Schema must be JSON object"]}

    # Required fields
    required = REQUIRED_FIELDS.get(schema_type, [])
    for field in required:
        if field not in schema or not schema[field]:
            issues.append(f"Missing required field: {field}")

    # Type-specific
    if schema_type == "Product":
        offers = schema.get("offers", {})
        if isinstance(offers, dict):
            if not offers.get("priceCurrency"):
                issues.append("Product.offers.priceCurrency missing")
            if not offers.get("price"):
                issues.append("Product.offers.price missing")
            if not offers.get("availability"):
                issues.append("Product.offers.availability missing")

    if schema_type == "FAQPage":
        main_entity = schema.get("mainEntity", [])
        if not main_entity:
            issues.append("FAQPage.mainEntity must contain at least 1 Question")
        for q in main_entity:
            if not q.get("name") or not q.get("acceptedAnswer", {}).get("text"):
                issues.append("FAQPage Question missing name or acceptedAnswer.text")
                break

    if schema_type == "Article":
        author = schema.get("author", {})
        if isinstance(author, dict) and not author.get("sameAs"):
            issues.append(
                "(suggestion) Article.author.sameAs missing — weak E-E-A-T signal"
            )

    return {
        "valid": len([i for i in issues if not i.startswith("(suggestion)")]) == 0,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Schema.org JSON-LD generator per /seo-strategist"
    )
    parser.add_argument("--type", required=True, help="Schema type")
    parser.add_argument("--metadata", help="YAML/JSON metadata file path", default=None)
    parser.add_argument(
        "--site-type",
        default="content_blog",
        help="Site type (governs FAQPage warning)",
    )
    parser.add_argument("--validate", action="store_true", help="Run tier 1 validation")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    schema_type = args.type

    # HowTo guard (DECISION-007)
    if schema_type in DEPRECATED_TYPES:
        result = {
            "rejected": True,
            "reason": f"{schema_type} schema rich result deprecated 2023 (Google).",
            "fallback_suggestion": "Article + nested ItemList preserves better. See references/schema-markup-guide-2026.md",
            "example_fallback": {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "...",
                "mainEntity": {
                    "@type": "ItemList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Step 1",
                            "url": "...",
                        },
                    ],
                },
            },
        }
        print(json.dumps(result, indent=2))
        return 2

    if schema_type not in SUPPORTED_TYPES:
        print(
            json.dumps(
                {
                    "error": f"Unsupported type: {schema_type}",
                    "supported": sorted(SUPPORTED_TYPES),
                }
            )
        )
        return 2

    meta = load_metadata(args.metadata) if args.metadata else {}

    builder = BUILDERS.get(schema_type)
    if not builder:
        print(json.dumps({"error": f"Builder not implemented for {schema_type}"}))
        return 2

    schema = builder(meta)

    # FAQPage eligibility warning (DECISION-006)
    warnings = []
    if schema_type == "FAQPage" and args.site_type not in FAQPAGE_ELIGIBLE_SITE_TYPES:
        warnings.append(
            f"⚠ FAQPage Google rich result NON eligible per site_type={args.site_type}. "
            "Schema mantenuto per LLM citation (ChatGPT/Perplexity/Claude) — Tier 1 GEO. "
            "Source: https://developers.google.com/search/docs/appearance/structured-data/faqpage"
        )

    result = {
        "schema_type": schema_type,
        "site_type": args.site_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "json_ld": schema,
        "warnings": warnings,
        "deployment_instructions": {
            "html_injection": '<script type="application/ld+json">'
            + json.dumps(schema)
            + "</script>",
            "wp_plugins_compatible": ["Yoast SEO", "Rank Math", "Schema Pro"],
            "next_js": "metadata API or <Script> tag in <Head>",
        },
    }

    if args.validate:
        result["validation"] = validate_schema(schema, schema_type)

    output_str = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Wrote {args.output}")
    else:
        print(output_str)

    if args.validate and not result["validation"]["valid"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
