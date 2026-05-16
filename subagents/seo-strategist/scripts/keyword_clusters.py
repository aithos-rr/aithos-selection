#!/usr/bin/env python3
"""keyword_clusters.py — Semantic clustering keyword + intent classification + opportunity scoring.

Input: lista keyword (CSV o args). Output cluster JSON con pillar/supporting/long-tail + intent + score.

Usage:
    python3 keyword_clusters.py --seed "ecommerce analytics" "shopify analytics" --geo italia --site-type saas_b2b
    python3 keyword_clusters.py --input keywords.csv --output cluster.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


# Intent classification rule-based
INTENT_PATTERNS = {
    "transactional": [
        r"\b(buy|comprare|acquistare|trial|signup|subscribe|abbonarsi|iscriversi|prezzo|costo|pricing|discount|sconto|offerta|deal|free|gratis)\b",
    ],
    "commercial": [
        r"\b(best|miglior|migliori|vs|versus|review|recensione|comparison|confronto|alternative|alternativa|top \d+)\b",
    ],
    "informational": [
        r"\b(how to|come|cosa|what is|che cos|guide|guida|tutorial|learn|imparare|spiegazione|introduction|introduzione)\b",
    ],
    "navigational": [
        r"\b(login|accedi|sign in|account|dashboard|app|home page)\b",
    ],
}

INTENT_WEIGHT = {
    "transactional": 1.5,
    "commercial": 1.5,
    "informational": 1.0,
    "navigational": 0.3,
}


# Stop words IT + EN (semplificato)
STOP_WORDS = set(
    """
il lo la i gli le un uno una di a da in con su per tra fra e o ma se non perché poiché
the a an of to in on with for at by from is are was were be been being will would could should
""".split()
)


def classify_intent(keyword: str) -> str:
    kw_lower = keyword.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, kw_lower):
                return intent
    # Default informational if no match
    return "informational"


def is_long_tail(keyword: str) -> bool:
    return len(keyword.split()) >= 4


def tokenize(keyword: str) -> list[str]:
    tokens = re.findall(r"\w+", keyword.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def cosine_similarity_bow(kw1: str, kw2: str) -> float:
    """Bag-of-words cosine similarity (fallback if sentence-transformers not available)."""
    t1 = Counter(tokenize(kw1))
    t2 = Counter(tokenize(kw2))
    if not t1 or not t2:
        return 0.0
    common = set(t1.keys()) & set(t2.keys())
    dot = sum(t1[w] * t2[w] for w in common)
    mag1 = math.sqrt(sum(c**2 for c in t1.values()))
    mag2 = math.sqrt(sum(c**2 for c in t2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def cluster_keywords(keywords: list[str], threshold: float = 0.5) -> list[dict]:
    """Greedy clustering bow-cosine. Each cluster = list of similar keywords."""
    clusters: list[list[str]] = []
    for kw in keywords:
        placed = False
        for cluster in clusters:
            # Compare to centroid (first item) for speed
            sim = cosine_similarity_bow(kw, cluster[0])
            if sim >= threshold:
                cluster.append(kw)
                placed = True
                break
        if not placed:
            clusters.append([kw])

    return [
        {"centroid": cluster[0], "size": len(cluster), "members": cluster}
        for cluster in clusters
    ]


def estimate_volume_qualitative(keyword: str, site_type: str) -> str:
    """Qualitative bucketing senza API. Heuristic."""
    word_count = len(keyword.split())
    has_brand = any(
        b in keyword.lower()
        for b in ("ahrefs", "semrush", "moz", "google", "shopify", "wordpress")
    )

    if word_count >= 5:
        return "low"  # ultra long-tail
    elif word_count >= 4:
        return "low" if not has_brand else "medium"
    elif word_count == 3:
        return "medium"
    elif word_count == 2:
        return "high" if has_brand else "medium"
    else:  # 1 word
        return "high" if not has_brand else "very_high"


def estimate_difficulty_qualitative(keyword: str) -> str:
    """Qualitative bucketing senza API."""
    word_count = len(keyword.split())
    if word_count >= 4:
        return "low"
    elif word_count == 3:
        return "medium"
    else:
        return "high"


VOLUME_NUMERIC = {"very_high": 10000, "high": 2500, "medium": 500, "low": 100}
DIFFICULTY_NUMERIC = {"low": 20, "medium": 45, "high": 75}


def opportunity_score(volume_label: str, difficulty_label: str, intent: str) -> float:
    volume = VOLUME_NUMERIC.get(volume_label, 100)
    difficulty = DIFFICULTY_NUMERIC.get(difficulty_label, 75)
    intent_w = INTENT_WEIGHT.get(intent, 1.0)
    score = math.log10(volume + 1) * 20 * (100 - difficulty) / 100 * intent_w
    return round(score, 1)


def load_keywords(input_path: str | None, seed: list[str]) -> list[str]:
    keywords = list(seed)
    if input_path:
        path = Path(input_path)
        if not path.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return keywords
        with open(path, "r", encoding="utf-8") as f:
            # Try CSV first
            sample = f.read(1024)
            f.seek(0)
            if "," in sample or "\t" in sample:
                reader = csv.DictReader(f)
                if reader.fieldnames and "keyword" in reader.fieldnames:
                    for row in reader:
                        keywords.append(row["keyword"])
                else:
                    f.seek(0)
                    # plain CSV one column
                    for line in f:
                        kw = line.strip().split(",")[0]
                        if kw and kw.lower() != "keyword":
                            keywords.append(kw)
            else:
                # one keyword per line
                for line in f:
                    kw = line.strip()
                    if kw:
                        keywords.append(kw)
    return list(dict.fromkeys(keywords))  # dedupe, preserve order


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keyword semantic clustering per /seo-strategist"
    )
    parser.add_argument("--seed", nargs="*", default=[], help="Seed keyword(s)")
    parser.add_argument("--input", help="CSV/text file with keywords")
    parser.add_argument("--geo", default="italia")
    parser.add_argument("--site-type", default="content_blog")
    parser.add_argument(
        "--threshold", type=float, default=0.5, help="Cosine similarity threshold"
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    keywords = load_keywords(args.input, args.seed)

    if not keywords:
        print(json.dumps({"error": "No keywords provided. Use --seed or --input"}))
        return 2

    if len(keywords) < 3:
        print(
            json.dumps(
                {
                    "error": "insufficient_evidence",
                    "detail": f"Got {len(keywords)} keyword(s). Suggest expand seed or provide --input CSV with more keywords.",
                    "keywords": keywords,
                }
            )
        )
        return 2

    clusters_raw = cluster_keywords(keywords, threshold=args.threshold)

    enriched_clusters = []
    long_tail_keywords = []

    for cluster in clusters_raw:
        members_enriched = []
        for kw in cluster["members"]:
            intent = classify_intent(kw)
            volume = estimate_volume_qualitative(kw, args.site_type)
            difficulty = estimate_difficulty_qualitative(kw)
            score = opportunity_score(volume, difficulty, intent)
            entry = {
                "keyword": kw,
                "intent": intent,
                "volume_estimate_label": volume,
                "difficulty_estimate_label": difficulty,
                "opportunity_score": score,
                "source": "qualitative_bucketing",
            }
            members_enriched.append(entry)
            if is_long_tail(kw):
                long_tail_keywords.append(entry)

        # Pick pillar = highest opportunity score
        members_enriched.sort(key=lambda x: x["opportunity_score"], reverse=True)
        if members_enriched:
            pillar = members_enriched[0]
            supporting = members_enriched[1:]
            enriched_clusters.append(
                {
                    "pillar_keyword": pillar["keyword"],
                    "pillar_intent": pillar["intent"],
                    "pillar_volume_estimate": pillar["volume_estimate_label"],
                    "pillar_difficulty_estimate": pillar["difficulty_estimate_label"],
                    "pillar_opportunity_score": pillar["opportunity_score"],
                    "supporting_keywords": supporting,
                    "cluster_size": cluster["size"],
                }
            )

    result = {
        "seed_keywords": args.seed,
        "geo_target": args.geo,
        "site_type": args.site_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_sources": ["qualitative_bucketing"],
        "clusters": enriched_clusters,
        "long_tail_keywords": long_tail_keywords,
        "anti_hallucination_flags": {
            "volume_estimated_no_api": True,
            "difficulty_estimated_no_api": True,
            "fallback_clustering_used": True,
            "note": "No Ahrefs/SEMrush/Moz API key present. Volume/difficulty are qualitative buckets. Run with API for precise numbers.",
        },
    }

    output_str = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Wrote {args.output}")
    else:
        print(output_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
