#!/usr/bin/env python3
"""validate_input.py — Schema validation per input agent /seo-strategist.

Valida domain reachability, sitemap accessible, robots.txt readable, competitor list well-formed.
Output JSON con campo `valid: bool` + `issues: []`.

Usage:
    python3 validate_input.py --domain example.com
    python3 validate_input.py --domain example.com --sitemap https://example.com/sitemap.xml --competitors a.com,b.com
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print(
        json.dumps(
            {
                "valid": False,
                "issues": ["requests not installed: pip install -r requirements.txt"],
            }
        )
    )
    sys.exit(1)


DOMAIN_RE = re.compile(r"^(?!-)([A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,}$")
TIMEOUT = 10


def validate_domain(domain: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not DOMAIN_RE.match(domain):
        issues.append(f"Domain syntax invalid: {domain}")
        return False, issues

    url = f"https://{domain}"
    try:
        r = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": "seo-strategist-audit/1.0"},
        )
        if r.status_code >= 500:
            issues.append(f"Domain {domain} returned HTTP {r.status_code}")
        if not r.url.startswith("https://"):
            issues.append(
                f"Domain {domain} did not redirect to HTTPS — security/SEO concern"
            )
    except requests.exceptions.SSLError:
        issues.append(f"Domain {domain} HTTPS certificate invalid")
    except requests.exceptions.ConnectionError:
        issues.append(f"Domain {domain} unreachable (connection error)")
    except requests.exceptions.Timeout:
        issues.append(f"Domain {domain} timed out (>{TIMEOUT}s)")
    except Exception as e:  # noqa: BLE001
        issues.append(f"Domain {domain} unexpected error: {e}")

    return (len(issues) == 0), issues


def validate_robots(domain: str) -> tuple[bool, list[str], dict]:
    issues: list[str] = []
    info = {
        "present": False,
        "blocks_all": False,
        "gpt_allowed": None,
        "perplexity_allowed": None,
        "sitemap_referenced": False,
    }

    url = f"https://{domain}/robots.txt"
    try:
        r = requests.get(
            url, timeout=TIMEOUT, headers={"User-Agent": "seo-strategist-audit/1.0"}
        )
        if r.status_code == 200:
            info["present"] = True
            text = r.text.lower()
            # Crude global disallow check
            for block in re.split(r"user-agent:\s*\*", text)[1:]:
                if re.search(r"^\s*disallow:\s*/\s*$", block, re.MULTILINE):
                    info["blocks_all"] = True
                    issues.append(
                        "robots.txt has global Disallow: / — site blocked from indexing"
                    )
                    break
            info["gpt_allowed"] = (
                "user-agent: gptbot" not in text or "disallow: /" not in text
            )
            info["perplexity_allowed"] = (
                "user-agent: perplexitybot" not in text or "disallow: /" not in text
            )
            info["sitemap_referenced"] = "sitemap:" in text
        elif r.status_code == 404:
            issues.append(
                "robots.txt missing (404) — Google will crawl all by default but explicit file recommended"
            )
        else:
            issues.append(f"robots.txt returned HTTP {r.status_code}")
    except Exception as e:  # noqa: BLE001
        issues.append(f"robots.txt fetch error: {e}")

    return (not info["blocks_all"]), issues, info


def validate_sitemap(
    domain: str, sitemap_url: str | None
) -> tuple[bool, list[str], dict]:
    issues: list[str] = []
    info = {"present": False, "url": None, "url_count": 0}

    candidates = (
        [sitemap_url]
        if sitemap_url
        else [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemap-index.xml",
        ]
    )
    candidates = [c for c in candidates if c]

    for url in candidates:
        try:
            r = requests.get(
                url, timeout=TIMEOUT, headers={"User-Agent": "seo-strategist-audit/1.0"}
            )
            if r.status_code == 200 and (
                "<urlset" in r.text or "<sitemapindex" in r.text
            ):
                info["present"] = True
                info["url"] = url
                info["url_count"] = r.text.count("<loc>")
                break
        except Exception:  # noqa: BLE001
            continue

    if not info["present"]:
        issues.append(f"Sitemap not found at {candidates}")

    return info["present"], issues, info


def validate_competitors(competitors: list[str]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not competitors:
        return True, issues
    if len(competitors) > 5:
        issues.append(
            f"Max 5 competitors per audit run (got {len(competitors)}). Suggest splitting into batches."
        )
    for c in competitors:
        c = c.strip()
        if not DOMAIN_RE.match(c):
            issues.append(f"Competitor domain invalid syntax: {c}")
    return (len(issues) == 0), issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate input for /seo-strategist audit run"
    )
    parser.add_argument(
        "--domain", required=True, help="Target domain (e.g., example.com)"
    )
    parser.add_argument("--sitemap", help="Optional sitemap URL", default=None)
    parser.add_argument(
        "--competitors", help="Comma-separated competitor domains (max 5)", default=""
    )
    parser.add_argument("--output", help="Output JSON file path", default=None)
    args = parser.parse_args()

    competitors = [c.strip() for c in args.competitors.split(",") if c.strip()]

    domain_ok, domain_issues = validate_domain(args.domain)
    robots_ok, robots_issues, robots_info = validate_robots(args.domain)
    sitemap_ok, sitemap_issues, sitemap_info = validate_sitemap(
        args.domain, args.sitemap
    )
    competitors_ok, competitors_issues = validate_competitors(competitors)

    all_issues = domain_issues + robots_issues + sitemap_issues + competitors_issues
    valid_overall = domain_ok and robots_ok and sitemap_ok and competitors_ok

    result = {
        "valid": valid_overall,
        "domain_check": {"ok": domain_ok, "issues": domain_issues},
        "robots_check": {"ok": robots_ok, "issues": robots_issues, "info": robots_info},
        "sitemap_check": {
            "ok": sitemap_ok,
            "issues": sitemap_issues,
            "info": sitemap_info,
        },
        "competitors_check": {
            "ok": competitors_ok,
            "issues": competitors_issues,
            "count": len(competitors),
        },
        "issues_total": all_issues,
    }

    output_str = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Wrote {args.output}")
    else:
        print(output_str)

    return 0 if valid_overall else 2


if __name__ == "__main__":
    sys.exit(main())
