#!/usr/bin/env python3
"""content_brief_gen.py — Genera content brief markdown per content team.

Input: target keyword + intent + optional competitor URL list.
Output: brief markdown structurato (E-E-A-T checklist + outline + GEO patterns + schema recommendation).

Usage:
    python3 content_brief_gen.py --keyword "ecommerce analytics guide" --intent informational --site-type saas_b2b
    python3 content_brief_gen.py --input briefs.csv --output-dir output/
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path


def render_brief(
    keyword: str,
    intent: str,
    site_type: str,
    geo_priority: str = "secondary",
    pillar_url: str | None = None,
    competitor_urls: list[str] | None = None,
    word_count_target: int = 1500,
    schema_recommendation: str | None = None,
) -> str:
    competitor_urls = competitor_urls or []

    if not schema_recommendation:
        schema_map = {
            "saas_b2b": "Article + Person (author) + Organization (publisher)",
            "ecommerce": "Product + AggregateRating + BreadcrumbList + Offer",
            "content_blog": "Article + Person + FAQPage (Q&A in body)",
            "local": "LocalBusiness + Article (if blog) + BreadcrumbList",
            "agency": "Article + Organization + Person (author)",
        }
        schema_recommendation = schema_map.get(
            site_type, "Article + Person + Organization"
        )

    geo_block = ""
    if geo_priority in ("priority", "secondary"):
        geo_block = """
## GEO patterns (LLM citation optimization)

- [ ] H2 in formato domanda diretta (boost Claude/Perplexity citation)
- [ ] 1 citation autorevole ogni 200-300 parole (boost ChatGPT credibility)
- [ ] Author bio con sameAs LinkedIn/Twitter (E-E-A-T + LLM trust)
- [ ] dateModified visibile + schema (Perplexity freshness <90gg)
- [ ] Bulleted lists frequenti (Perplexity preference)
- [ ] Single-paragraph definitions ad inizio sezione (ChatGPT preference)
- [ ] Original data o quote unique (Wikipedia-grade content potential)
"""

    competitor_block = ""
    if competitor_urls:
        competitor_block = "## Competitor benchmark\n\n"
        for i, url in enumerate(competitor_urls, 1):
            competitor_block += (
                f"- Top {i}: {url} (analizza word count + outline + key sections)\n"
            )
        competitor_block += "\n"

    pillar_block = (
        f"\n**Internal link target**: {pillar_url}\n"
        if pillar_url
        else "\n**Internal link target**: TBD (pillar page)\n"
    )

    today = datetime.now().strftime("%Y-%m-%d")

    brief = f"""# Brief: {keyword}

**Generated**: {today}
**Target keyword**: `{keyword}`
**Search intent**: {intent}
**Site type**: {site_type}
**Word count target**: ~{word_count_target} word (top 3 ranking competitor + 20% bonus)
**E-E-A-T signal needed**: author byline + dateModified visible + 2-3 expert quote inline + 1 original data point

{competitor_block}## Content outline (proposed)

- **H1**: {keyword.capitalize()}
- **Intro** (~150 word): hook + problem statement + value promise + TL;DR
- **H2 question-format**: Cos'è/Quali sono/Perché... ({keyword})?
- **H2**: Come {keyword} funziona — overview
- **H2**: 5 best practice per {keyword}
- **H2**: Errori comuni da evitare
- **H2**: Tool consigliati (basato budget)
- **H2 (FAQ)**: Domande frequenti
- **Conclusione + CTA**: {pillar_block.strip()}

## Schema recommendation

{schema_recommendation}

⚠ Validate via [Schema.org Validator](https://validator.schema.org/) + [Google Rich Results Test](https://search.google.com/test/rich-results) prima di deploy.
{geo_block}
## SEO checklist

- [ ] Title 50-60 char includes primary keyword
- [ ] Meta description 130-155 char with CTA
- [ ] H1 exact match keyword (1 only)
- [ ] H2 hierarchy logica (3-7 H2)
- [ ] 3-5 internal link contextual
- [ ] 2-3 external citation autorevole
- [ ] Image: 1 hero + 2-3 supporting, alt text descriptive
- [ ] Schema validato pre-deploy
- [ ] dateModified updated post-publish
- [ ] Permalink short, hyphens, lowercase

## E-E-A-T checklist

- [ ] Author byline visibile (con bio + credentials)
- [ ] Schema Person con sameAs LinkedIn/Twitter
- [ ] Sources cited inline (no "click here", anchor descriptive)
- [ ] Original data o expert quote (information gain signal)
- [ ] Disclosure AI assistance se used (Helpful Content "How" framework)

## Helpful Content red flag check

- [ ] Content NOT mass-produced (single topic depth, not breadth random)
- [ ] Original perspective o data (not re-hash top 10)
- [ ] User-first (would I bookmark this? share with friend?)
- [ ] No keyword stuffing
- [ ] No boilerplate >70%

## Anti-pattern da evitare

- ❌ Generato AI senza disclosure
- ❌ Re-hash top 10 senza original insight
- ❌ Keyword stuffing in body
- ❌ HowTo schema (deprecated 2023)
- ❌ Promesse traffic specifiche (e.g., "+200%")
- ❌ Citation a fonti non-autorevoli o random blog

## Definition of Done

- [ ] Outline approvato
- [ ] First draft scritto (target word count)
- [ ] Editorial review pass
- [ ] Schema validato
- [ ] Internal link audit pass
- [ ] Image optimized (WebP, lazy load, alt)
- [ ] Published + dateModified updated
- [ ] Search Console URL Inspection requested

---

*Brief generated by /seo-strategist content_brief_gen.py*
"""
    return brief


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Content brief generator per /seo-strategist"
    )
    parser.add_argument("--keyword", help="Target keyword")
    parser.add_argument(
        "--intent",
        default="informational",
        choices=["informational", "navigational", "transactional", "commercial"],
    )
    parser.add_argument("--site-type", default="content_blog")
    parser.add_argument(
        "--geo-priority", default="secondary", choices=["priority", "secondary", "skip"]
    )
    parser.add_argument("--pillar-url", default=None)
    parser.add_argument(
        "--competitor-urls", default="", help="Comma-separated competitor URLs"
    )
    parser.add_argument("--word-count-target", type=int, default=1500)
    parser.add_argument(
        "--input", help="CSV with brief specs (keyword,intent,site_type,competitors)"
    )
    parser.add_argument("--output", help="Single output path", default=None)
    parser.add_argument("--output-dir", help="Output directory for batch", default=None)
    args = parser.parse_args()

    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(json.dumps({"error": f"Input not found: {args.input}"}))
            return 2
        out_dir = Path(args.output_dir or "output")
        out_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kw = row.get("keyword") or row.get("Keyword")
                if not kw:
                    continue
                competitors = [
                    c.strip()
                    for c in (row.get("competitors") or "").split(",")
                    if c.strip()
                ]
                brief = render_brief(
                    kw,
                    intent=row.get("intent", "informational"),
                    site_type=row.get("site_type", args.site_type),
                    geo_priority=row.get("geo_priority", args.geo_priority),
                    competitor_urls=competitors,
                    word_count_target=int(
                        row.get("word_count_target", args.word_count_target)
                    ),
                )
                slug = kw.lower().replace(" ", "-").replace("/", "-")[:60]
                out_path = out_dir / f"brief-{slug}.md"
                out_path.write_text(brief, encoding="utf-8")
                count += 1
        print(json.dumps({"briefs_generated": count, "output_dir": str(out_dir)}))
        return 0

    if not args.keyword:
        print(json.dumps({"error": "Provide --keyword or --input"}))
        return 2

    competitor_urls = [c.strip() for c in args.competitor_urls.split(",") if c.strip()]
    brief = render_brief(
        args.keyword,
        args.intent,
        args.site_type,
        geo_priority=args.geo_priority,
        pillar_url=args.pillar_url,
        competitor_urls=competitor_urls,
        word_count_target=args.word_count_target,
    )

    if args.output:
        Path(args.output).write_text(brief, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(brief)

    return 0


if __name__ == "__main__":
    sys.exit(main())
