#!/usr/bin/env python3
"""audit_onpage.py — On-page technical SEO audit per URL/dominio.

Fetch HTML + parse + check schema + canonical + hreflang + meta + headings.
Output JSON con issues priority list (P0/P1/P2).

Usage:
    python3 audit_onpage.py --url https://example.com/page
    python3 audit_onpage.py --domain example.com --sample-size 50
    python3 audit_onpage.py --url https://example.com/page --geo-mode --target-platforms chatgpt,perplexity,claude,gemini
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print(json.dumps({"error": "deps missing: pip install -r requirements.txt"}))
    sys.exit(1)


TIMEOUT = 15
RATE_LIMIT_SECONDS = 2  # 1 req per 2s default
USER_AGENT = (
    "seo-strategist-audit/1.0 (+https://github.com/filippogreco/claude-skills-learnn)"
)


def fetch_url(url: str) -> tuple[str | None, dict]:
    info = {"status_code": None, "final_url": None, "content_length": 0}
    try:
        r = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        info["status_code"] = r.status_code
        info["final_url"] = r.url
        info["content_length"] = len(r.text)
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r.text, info
        return None, info
    except Exception as e:  # noqa: BLE001
        info["error"] = str(e)
        return None, info


def audit_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else None
    title_len = len(title) if title else 0

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_content = meta_desc.get("content", "").strip() if meta_desc else None
    meta_desc_len = len(meta_desc_content) if meta_desc_content else 0

    # Robots meta
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    robots_content = robots_meta.get("content", "").lower() if robots_meta else ""
    is_noindex = "noindex" in robots_content
    is_nofollow = "nofollow" in robots_content

    # Canonical
    canonical = soup.find("link", attrs={"rel": "canonical"})
    canonical_href = canonical.get("href") if canonical else None

    # Hreflang
    hreflangs = []
    for tag in soup.find_all("link", attrs={"rel": "alternate"}):
        if tag.get("hreflang"):
            hreflangs.append({"hreflang": tag.get("hreflang"), "href": tag.get("href")})

    # Headings
    h1_list = [h.get_text().strip() for h in soup.find_all("h1")]
    h2_list = [h.get_text().strip() for h in soup.find_all("h2")]
    h3_list = [h.get_text().strip() for h in soup.find_all("h3")]

    # Word count (approximate)
    body = soup.find("body")
    body_text = body.get_text(separator=" ", strip=True) if body else ""
    word_count = len(body_text.split())

    # Images alt
    images = soup.find_all("img")
    img_count = len(images)
    img_with_alt = sum(1 for i in images if i.get("alt", "").strip())
    img_alt_pct = (img_with_alt / img_count * 100) if img_count else 100

    # Schema (JSON-LD)
    schemas = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                for d in data:
                    if isinstance(d, dict):
                        schemas.append(d.get("@type", "Unknown"))
            elif isinstance(data, dict):
                schemas.append(data.get("@type", "Unknown"))
        except json.JSONDecodeError:
            schemas.append("INVALID_JSON")

    # Internal vs external links
    parsed = urlparse(url)
    domain = parsed.netloc
    internal_links = 0
    external_links = 0
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if (
            href.startswith("#")
            or href.startswith("mailto:")
            or href.startswith("tel:")
        ):
            continue
        if href.startswith("/") or domain in href:
            internal_links += 1
        elif href.startswith("http"):
            external_links += 1

    # Q-format H2 (GEO signal)
    q_format_h2 = sum(
        1
        for h in h2_list
        if h.endswith("?")
        or any(
            h.lower().startswith(qw)
            for qw in (
                "come ",
                "cosa ",
                "perché ",
                "what ",
                "how ",
                "why ",
                "when ",
                "where ",
                "qual ",
                "quali ",
            )
        )
    )

    # External citation count (proxy for citation density)
    external_authoritative = 0
    AUTHORITY_DOMAINS = (
        "wikipedia.org",
        "google.com",
        "developers.google.com",
        "schema.org",
        "web.dev",
        "moz.com",
        "ahrefs.com",
        "searchengineland.com",
        "backlinko.com",
        ".gov",
        ".edu",
    )
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if any(d in href for d in AUTHORITY_DOMAINS):
            external_authoritative += 1

    citation_density = (
        external_authoritative / max(word_count, 1)
    ) * 250  # citations per 250 word

    # Author detection
    has_author_byline = bool(
        soup.find(attrs={"class": re.compile(r"author|byline", re.I)})
    )
    has_person_schema = "Person" in schemas

    # Issues priority
    issues = []
    if not title:
        issues.append(
            {"priority": "P0", "issue": "title_missing", "fix": "Add <title> tag"}
        )
    elif title_len < 10 or title_len > 70:
        issues.append(
            {
                "priority": "P2",
                "issue": "title_length",
                "detail": f"len={title_len}",
                "fix": "Aim 30-60 char",
            }
        )

    if not meta_desc_content:
        issues.append(
            {
                "priority": "P1",
                "issue": "meta_description_missing",
                "fix": "Add meta description 130-155 char",
            }
        )
    elif meta_desc_len < 50 or meta_desc_len > 160:
        issues.append(
            {
                "priority": "P2",
                "issue": "meta_description_length",
                "detail": f"len={meta_desc_len}",
            }
        )

    if is_noindex:
        issues.append(
            {
                "priority": "P0",
                "issue": "robots_noindex",
                "fix": "Verify intentional; if not, remove noindex meta",
            }
        )

    if not canonical_href:
        issues.append(
            {
                "priority": "P1",
                "issue": "canonical_missing",
                "fix": 'Add <link rel="canonical"> tag',
            }
        )

    if len(h1_list) == 0:
        issues.append({"priority": "P1", "issue": "h1_missing", "fix": "Add 1 H1 tag"})
    elif len(h1_list) > 1:
        issues.append(
            {
                "priority": "P2",
                "issue": "h1_multiple",
                "detail": f"count={len(h1_list)}",
                "fix": "Use only 1 H1",
            }
        )

    if word_count < 300:
        issues.append(
            {
                "priority": "P1",
                "issue": "thin_content",
                "detail": f"wc={word_count}",
                "fix": "Expand content >500 word ideal",
            }
        )

    if not schemas:
        issues.append(
            {
                "priority": "P1",
                "issue": "schema_missing",
                "fix": "Add JSON-LD schema (Article/Product/etc.)",
            }
        )
    elif "INVALID_JSON" in schemas:
        issues.append(
            {
                "priority": "P0",
                "issue": "schema_invalid",
                "fix": "Fix JSON syntax in <script type=application/ld+json>",
            }
        )

    if "HowTo" in schemas:
        issues.append(
            {
                "priority": "P2",
                "issue": "howto_deprecated",
                "fix": "HowTo deprecated 2023; fallback Article + ItemList",
            }
        )

    if img_alt_pct < 80:
        issues.append(
            {
                "priority": "P2",
                "issue": "image_alt_missing",
                "detail": f"pct={img_alt_pct:.0f}%",
                "fix": "Add descriptive alt to all images",
            }
        )

    if not has_author_byline and not has_person_schema:
        issues.append(
            {
                "priority": "P2",
                "issue": "author_byline_missing",
                "fix": "Add author byline + Person schema (E-E-A-T signal)",
            }
        )

    return {
        "url": url,
        "title": title,
        "title_len": title_len,
        "meta_description_len": meta_desc_len,
        "is_noindex": is_noindex,
        "is_nofollow": is_nofollow,
        "canonical_href": canonical_href,
        "hreflangs": hreflangs,
        "h1_count": len(h1_list),
        "h2_count": len(h2_list),
        "h2_q_format_count": q_format_h2,
        "h2_q_format_pct": (q_format_h2 / max(len(h2_list), 1)) * 100,
        "h3_count": len(h3_list),
        "word_count": word_count,
        "img_count": img_count,
        "img_alt_pct": img_alt_pct,
        "schemas": schemas,
        "internal_links": internal_links,
        "external_links": external_links,
        "external_authoritative_citations": external_authoritative,
        "citation_density_per_250w": citation_density,
        "has_author_byline": has_author_byline,
        "has_person_schema": has_person_schema,
        "issues": issues,
    }


def compute_geo_score(audit: dict) -> dict:
    """Compute GEO score 0-100 per skill geo-optimizer."""
    components = {
        "q_format_h2": min(audit["h2_q_format_pct"] / 50, 1.0),
        "citation_density": min(audit["citation_density_per_250w"], 1.0),
        "schema_completeness": min(
            len([s for s in audit["schemas"] if s != "INVALID_JSON"]) / 3, 1.0
        ),
        "author_authority": (0.5 if audit["has_author_byline"] else 0)
        + (0.5 if audit["has_person_schema"] else 0),
        "freshness": 0.0,  # requires dateModified parsing — deferred
        "llms_txt_presence": 0.0,  # checked separately
        "bulleted_content": 0.5,  # heuristic, would need <ul>/<ol> count
    }
    weights = {
        "q_format_h2": 15,
        "citation_density": 20,
        "schema_completeness": 20,
        "author_authority": 15,
        "freshness": 10,
        "llms_txt_presence": 10,
        "bulleted_content": 10,
    }
    score = sum(components[k] * weights[k] for k in components)
    return {"geo_score": round(score, 1), "components": components, "weights": weights}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="On-page SEO audit per /seo-strategist"
    )
    parser.add_argument("--url", help="Single URL to audit")
    parser.add_argument("--domain", help="Domain root (audit homepage + sample)")
    parser.add_argument(
        "--sample-size", type=int, default=1, help="Sample size if domain"
    )
    parser.add_argument("--geo-mode", action="store_true", help="Compute GEO score")
    parser.add_argument(
        "--target-platforms", default="chatgpt,perplexity,claude,gemini"
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if not args.url and not args.domain:
        print(json.dumps({"error": "Provide --url or --domain"}))
        return 2

    target_url = args.url or f"https://{args.domain}"
    html, fetch_info = fetch_url(target_url)

    if not html:
        result = {"error": "Failed to fetch", "fetch_info": fetch_info}
        out = json.dumps(result, indent=2)
        print(out)
        return 2

    audit = audit_page(target_url, html)
    audit["fetch_info"] = fetch_info

    if args.geo_mode:
        audit["geo"] = compute_geo_score(audit)
        audit["geo"]["target_platforms"] = args.target_platforms.split(",")
        audit["geo"]["disclaimer"] = (
            "Citation pattern % sono secondary source aggregati (Previsible report + aimagicx). "
            "Nessun vendor LLM pubblica primary citation stat ufficialmente."
        )

    out = json.dumps(audit, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote {args.output}")
    else:
        print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
