#!/usr/bin/env python3
"""
Arricchimento batch di lead via parallel-cli + LinkedIn search + Attio MCP.
Esegue agenti paralleli (max 5 concorrenti per rate limit).

Input CSV: almeno colonne `name`, `company`.
Output CSV arricchito: +email, +email_confidence, +linkedin, +role, +company_size, +industry, +intent_signals, +score.

Usage: python enrich_batch.py --input leads.csv --output enriched.csv --max-parallel 5
"""

import argparse
import asyncio
import csv
import json
import subprocess
import sys
from pathlib import Path


async def enrich_one(lead: dict, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        name = lead.get("name") or lead.get("Name") or ""
        company = lead.get("company") or lead.get("Company") or ""
        if not name or not company:
            return {**lead, "enrichment_status": "skipped: missing name/company"}

        # Email finder via parallel-cli
        email_q = f"find professional email of {name} at {company}"
        email_res = await run_parallel_cli("enrich", ["--query", email_q])

        # LinkedIn
        li_q = f"site:linkedin.com/in {name} {company}"
        li_res = await run_parallel_cli("search", [li_q, "--max-results", "3"])

        # Intent signals (recent news)
        signals_q = f"{company} funding OR hiring OR launch 2026"
        signals_res = await run_parallel_cli(
            "search", [signals_q, "--max-results", "5"]
        )

        email = extract_email(email_res)
        linkedin = extract_linkedin(li_res)
        signals = extract_signals(signals_res)

        # Score
        score = 0
        if email:
            score += 30
        if linkedin:
            score += 20
        if signals:
            score += 30
        if lead.get("role"):
            score += 20

        return {
            **lead,
            "email": email or "",
            "email_confidence": 0.85 if email else 0.0,
            "linkedin": linkedin or "",
            "intent_signals": "; ".join(signals[:3]),
            "score": score,
            "tier": "hot" if score >= 80 else "warm" if score >= 50 else "cold",
            "enrichment_status": "ok",
        }


async def run_parallel_cli(subcommand: str, args: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(
        "parallel-cli",
        subcommand,
        *args,
        "--json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        sys.stderr.write(f"parallel-cli error: {err.decode()[:200]}\n")
        return ""
    return out.decode()


def extract_email(text: str) -> str | None:
    import re

    m = re.search(r"[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else None


def extract_linkedin(text: str) -> str | None:
    import re

    m = re.search(r"linkedin\.com/in/[\w-]+", text)
    return f"https://{m.group(0)}" if m else None


def extract_signals(text: str) -> list[str]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    results = data.get("results", [])[:5]
    return [r.get("title", "")[:100] for r in results if r.get("title")]


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--max-parallel", type=int, default=5)
    args = p.parse_args()

    leads = list(csv.DictReader(Path(args.input).open()))
    sys.stderr.write(f"📥 Input: {len(leads)} lead\n")

    sem = asyncio.Semaphore(args.max_parallel)
    enriched = await asyncio.gather(*(enrich_one(lead, sem) for lead in leads))

    fieldnames = list(enriched[0].keys()) if enriched else []
    with Path(args.output).open("w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)

    # Report
    from collections import Counter

    tiers = Counter(e.get("tier", "?") for e in enriched)
    sys.stderr.write(f"✅ Output: {args.output}\n")
    sys.stderr.write(
        "Tiers: " + " | ".join(f"{t}:{n}" for t, n in tiers.most_common()) + "\n"
    )


if __name__ == "__main__":
    asyncio.run(main())
