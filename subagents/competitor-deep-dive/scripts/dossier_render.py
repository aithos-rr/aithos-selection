#!/usr/bin/env python3
"""Render dossier markdown deterministico per 1 competitor.

Usage: python scripts/dossier_render.py --slug make --positioning output/positioning_make.json [--tov output/tov_make.json] [--reviews output/reviews_make.json] [--gap-matrix output/gap-matrix.json] [--word-budget-dossier 1500] [--output-md research/dossier_make.md]
Author: Filippo Greco / competitor-deep-dive 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

DEFAULT_BUDGET_DOSSIER = 1500


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log.warning(f"JSON parse error {path}: {e}")
        return None


def render_section_positioning(positioning: dict) -> list:
    lines = ["## Positioning + Value Prop", ""]
    if positioning.get("stealth_detected"):
        lines.append(
            f"> WARNING: Stealth detected: {positioning.get('reason', 'homepage unavailable')}"
        )
        lines.append(
            f"> Suggerimento: {positioning.get('fallback_suggestion', 'retry 30gg')}"
        )
        return lines

    tagline = positioning.get("tagline", "_Not extracted_")
    tagline_url = (positioning.get("tagline_source") or {}).get("url", "#")
    lines.append(f'- **Tagline**: "{tagline}" ([source]({tagline_url}))')

    value_prop = positioning.get("value_prop", "_Not extracted_")
    vp_url = (positioning.get("value_prop_source") or {}).get("url", "#")
    lines.append(f'- **Value prop**: "{value_prop}" ([source]({vp_url}))')

    icp = positioning.get("icp_inferred", "_Not extracted_")
    lines.append(f"- **ICP inferred**: {icp}")
    icp_evidence = positioning.get("icp_evidence", [])
    if icp_evidence:
        ev = icp_evidence[0]
        lines.append(
            f'  - Evidence: "{ev.get("quote", "")}" ([{ev.get("url", "#")}]({ev.get("url", "#")}))'
        )

    diffs = positioning.get("differentiators", [])[:3]
    if diffs:
        lines.append("")
        lines.append("**3 differentiators**:")
        for i, d in enumerate(diffs, 1):
            ev_list = d.get("evidence") or [{}]
            ev = ev_list[0] if ev_list else {}
            lines.append(
                f'{i}. **{d.get("claim", "_Not extracted_")}** - "{ev.get("quote", "")}" ([source]({ev.get("url", "#")}))'
            )
    return lines


def render_section_tov(tov) -> list:
    lines = ["## Tone of Voice", ""]
    if not tov:
        lines.append(
            "> WARNING: ToV not analyzed (skip Quick scan o skill non eseguita)"
        )
        return lines

    if tov.get("insufficient_evidence"):
        lines.append(
            f"> WARNING: ToV unmeasurable: {tov.get('reason', 'insufficient corpus')}"
        )
        lines.append(f"> Suggerimento: {tov.get('suggestion', 'expand corpus')}")
        return lines

    scores = tov.get("scores", {})
    lines.append("**Scores 1-5 (Nielsen Norman 4-dim)**:")
    lines.append("")
    lines.append("| Dim | Score | Label |")
    lines.append("|-----|-------|-------|")
    dim_titles = {
        "formal_casual": "Formal-Casual",
        "funny_serious": "Funny-Serious",
        "respectful_irreverent": "Respectful-Irreverent",
        "enthusiastic_matter_of_fact": "Enthusiastic-Matter-of-fact",
    }
    for key, title in dim_titles.items():
        s = scores.get(key, {})
        lines.append(f"| {title} | {s.get('score', '?')} | {s.get('label', '_')} |")

    metrics = tov.get("derived_metrics", {})
    if metrics:
        lines.append("")
        lines.append("**Derived metrics**:")
        lines.append(f"- Jargon density: {metrics.get('jargon_density_pct', '?')}%")
        lines.append(
            f"- Pronoun ratio (we/you): {metrics.get('pronoun_ratio_we_you', '?')}"
        )
        lines.append(
            f"- Avg sentence length: {metrics.get('avg_sentence_length_words', '?')} parole"
        )
        lines.append(f"- CTA style: {metrics.get('cta_style', '?')}")
        lines.append(
            f"- Exclamation density: {metrics.get('exclamation_density_per_100w', '?')} per 100 parole"
        )

    return lines


def render_section_reviews(reviews) -> list:
    lines = ["## Reviews Sentiment", ""]
    if not reviews:
        lines.append(
            "> WARNING: Reviews not analyzed (skip Quick scan o skill non eseguita)"
        )
        return lines

    if reviews.get("insufficient_evidence"):
        lines.append(f"> WARNING: Reviews insufficient: {reviews.get('reason', '')}")
        lines.append(f"> Fallback: {reviews.get('fallback_suggestion', '')}")
        return lines

    total_obj = reviews.get("total_reviews_scraped", {})
    total = total_obj.get("total", "?") if isinstance(total_obj, dict) else total_obj
    actor = reviews.get("actor_used", "?")
    lines.append(f"**Sentiment breakdown** ({total} reviews via {actor}):")
    lines.append("")
    sb_obj = reviews.get("sentiment_breakdown", {})
    sb = sb_obj.get("weighted_avg", sb_obj) if isinstance(sb_obj, dict) else {}
    lines.append(f"- Positive: {sb.get('positive_pct', '?')}%")
    lines.append(f"- Neutral: {sb.get('neutral_pct', '?')}%")
    lines.append(f"- Negative: {sb.get('negative_pct', '?')}%")

    strengths = reviews.get("top_strengths", [])[:5]
    if strengths:
        lines.append("")
        lines.append("**Top 5 strengths**:")
        for i, s in enumerate(strengths, 1):
            ev_list = s.get("evidence") or [{}]
            ev = ev_list[0] if ev_list else {}
            lines.append(
                f'{i}. **{s.get("theme", "?")}** ({s.get("frequency", "?")} mentions) - "{ev.get("quote", "")}" ([{ev.get("review_id", "?")}]({ev.get("url", "#")}))'
            )

    weaknesses = reviews.get("top_weaknesses", [])[:5]
    if weaknesses:
        lines.append("")
        lines.append("**Top 5 weaknesses**:")
        for i, w in enumerate(weaknesses, 1):
            ev_list = w.get("evidence") or [{}]
            ev = ev_list[0] if ev_list else {}
            lines.append(
                f'{i}. **{w.get("theme", "?")}** ({w.get("frequency", "?")}) - "{ev.get("quote", "")}" ([{ev.get("review_id", "?")}]({ev.get("url", "#")}))'
            )

    jtbd = reviews.get("top_jtbd", [])[:3]
    if jtbd:
        lines.append("")
        lines.append("**Top 3 JTBD**:")
        for j in jtbd:
            lines.append(
                f"- {j.get('outcome', '?')} ({j.get('frequency', '?')} mentions)"
            )

    lhw = reviews.get("love_hate_want", {})
    if lhw:
        lines.append("")
        lines.append("**Love / Hate / Want**:")

        def _txt(lst):
            return ", ".join(
                (item.get("text", "") if isinstance(item, dict) else str(item))
                for item in lst[:3]
            )

        lines.append(f"- Love: {_txt(lhw.get('love', []))}")
        lines.append(f"- Hate: {_txt(lhw.get('hate', []))}")
        lines.append(f"- Want: {_txt(lhw.get('want', []))}")

    return lines


def render_section_gap(gap_matrix, competitor_slug: str) -> list:
    lines = ["## Gap vs cliente baseline", ""]
    if not gap_matrix:
        lines.append("> WARNING: Gap matrix not available (run gap-finder first)")
        return lines

    gaps = gap_matrix.get("gaps", [])[:5]
    if not gaps:
        lines.append("> No gaps identified")
        return lines

    for i, g in enumerate(gaps, 1):
        score = g.get("gap_score", "?")
        cat = g.get("category", "?")
        lines.append(
            f"{i}. **{g.get('title', '?')}** (score {score}, category {cat}) - {g.get('description', '?')}"
        )

    return lines


def enforce_word_budget(content: str, max_words: int) -> str:
    word_count = len(content.split())
    if word_count > max_words * 1.05:
        log.warning(f"Word budget exceeded: {word_count} > {max_words}, truncating")
        words = content.split()
        truncated = " ".join(words[:max_words])
        return (
            truncated
            + f"\n\n> WARNING: Truncated to fit {max_words}-word budget. Full data in artefatti JSON."
        )
    return content


def render_dossier(
    slug: str, positioning: dict, tov, reviews, gap_matrix, word_budget: int
) -> str:
    competitor_name = positioning.get("competitor", slug.title())
    domain = positioning.get("domain", "?")

    sections = [
        f"# {competitor_name}",
        "",
        f"> **Domain**: {domain} - **Scrape date**: {positioning.get('scrape_date', '?')}",
        "",
        "> **TL;DR (50-75 parole)**: _Da generare dal subagent dopo render template - sintesi 1 frase + 3 bullet basata su sezioni sotto._",
        "",
    ]

    sections.extend(render_section_positioning(positioning))
    sections.append("")
    sections.extend(render_section_tov(tov))
    sections.append("")
    sections.extend(render_section_reviews(reviews))
    sections.append("")
    sections.extend(render_section_gap(gap_matrix, slug))
    sections.append("")
    sections.append("---")
    sections.append("")
    sections.append(
        f"_Sources: {positioning.get('domain', '?')}, scrape via {positioning.get('scraper_used', 'playwright_mcp')}, reviews via {(reviews or {}).get('actor_used', 'n/a')}_"
    )

    content = "\n".join(sections)
    return enforce_word_budget(content, word_budget)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render dossier markdown")
    parser.add_argument("--slug", required=True, help="Competitor slug (e.g. make)")
    parser.add_argument("--positioning", required=True, help="Path positioning JSON")
    parser.add_argument("--tov", help="Path tov JSON")
    parser.add_argument("--reviews", help="Path reviews JSON")
    parser.add_argument("--gap-matrix", help="Path gap-matrix JSON")
    parser.add_argument(
        "--word-budget-dossier", type=int, default=DEFAULT_BUDGET_DOSSIER
    )
    parser.add_argument(
        "--output-md", help="Output path (default: research/dossier_<slug>.md)"
    )
    args = parser.parse_args()

    positioning = load_json(args.positioning)
    if not positioning:
        print(
            json.dumps({"error": f"positioning required: {args.positioning}"}),
            file=sys.stderr,
        )
        return 1

    tov = load_json(args.tov) if args.tov else None
    reviews = load_json(args.reviews) if args.reviews else None
    gap_matrix = load_json(args.gap_matrix) if args.gap_matrix else None

    content = render_dossier(
        args.slug, positioning, tov, reviews, gap_matrix, args.word_budget_dossier
    )

    output_path = Path(args.output_md or f"research/dossier_{args.slug}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    word_count = len(content.split())
    print(
        json.dumps(
            {
                "ok": True,
                "output_path": str(output_path),
                "word_count": word_count,
                "word_budget": args.word_budget_dossier,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
