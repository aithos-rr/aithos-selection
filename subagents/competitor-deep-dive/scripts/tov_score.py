#!/usr/bin/env python3
"""Calcola Tone of Voice 4-dim Nielsen Norman + 5 metriche derivate da corpus testuale.

Usage: python scripts/tov_score.py --corpus output/corpus.txt [--min-words 200] [--output output/tov.json]
Author: Filippo Greco / competitor-deep-dive 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

# Jargon list — tech + business + SaaS B2B
JARGON_TERMS = {
    "API",
    "SDK",
    "SAAS",
    "B2B",
    "ROI",
    "KPI",
    "OKR",
    "SOC2",
    "GDPR",
    "OAUTH",
    "REST",
    "GRAPHQL",
    "MLOPS",
    "DEVOPS",
    "CI/CD",
    "RBAC",
    "JWT",
    "SLA",
    "SLO",
    "DAU",
    "MAU",
    "CRM",
    "ERP",
    "BI",
    "ETL",
    "ELT",
    "DATALAKE",
    "DATAWAREHOUSE",
    "MICROSERVICES",
    "K8S",
    "KUBERNETES",
    "DOCKER",
    "AWS",
    "GCP",
    "AZURE",
    "ML",
    "AI",
    "LLM",
    "NLP",
    "OCR",
    "RAG",
    "EMBEDDING",
    "VECTOR",
    "TRANSFORMER",
    "TLS",
    "SSL",
    "VPN",
    "VPC",
    "IAM",
    "SAML",
    "SSO",
    "MFA",
    "2FA",
    "WEBHOOK",
    "POLLING",
    "PAGINATION",
    "RATE-LIMIT",
    "RATE-LIMITED",
    "ARR",
    "MRR",
    "CAC",
    "LTV",
    "NRR",
    "GRR",
    "NPS",
    "CSAT",
    "PMF",
    "UX",
    "UI",
    "DX",
    "PLG",
    "GTM",
    "ICP",
    "TCV",
    "ACV",
    "EBITDA",
}

CONTRACTIONS = re.compile(
    r"\b(don't|can't|won't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|"
    r"doesn't|didn't|wouldn't|couldn't|shouldn't|mustn't|let's|we're|you're|"
    r"they're|i'm|i've|we've|you've|they've|i'll|we'll|you'll|they'll|i'd|we'd|"
    r"you'd|they'd|here's|there's|that's|what's|who's|how's|where's|when's)\b",
    re.IGNORECASE,
)

CASUAL_LEXICON = {
    "hi",
    "hey",
    "yo",
    "stuff",
    "kinda",
    "gonna",
    "wanna",
    "yep",
    "yup",
    "ok",
    "okay",
    "lol",
    "haha",
    "uhh",
    "umm",
    "wow",
    "whoa",
    "oops",
}

PROVOCATIVE_LEXICON = {
    "damn",
    "screw",
    "kill",
    "smash",
    "hate",
    "suck",
    "garbage",
    "bullshit",
    "fuck",
    "hell",
    "wtf",
    "crap",
}

INTERJECTIONS = re.compile(
    r"\b(oops|whoa|wow|yay|hey|hi|hooray|argh|ugh|phew)\b", re.IGNORECASE
)

EMOJI_REGEX = re.compile(
    "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
    "\U0001f700-\U0001f77f\U0001f780-\U0001f7ff\U0001f800-\U0001f8ff"
    "\U0001f900-\U0001f9ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff"
    "☀-⛿✀-➿]"
)

CTA_IMPERATIVE = [
    "sign up",
    "get started",
    "try",
    "buy now",
    "download",
    "start",
    "book",
    "request",
    "claim",
    "activate",
    "join",
    "subscribe",
]
CTA_INVITANTE = [
    "learn more",
    "see how",
    "discover",
    "explore",
    "want to",
    "curious about",
    "read more",
    "find out",
    "watch the",
    "tell me more",
]


def compute_metrics(corpus: str) -> dict:
    """Compute 5 derived metrics."""
    words = re.findall(r"\b\w+\b", corpus)
    total_words = len(words)
    if total_words == 0:
        return {"error": "empty corpus"}

    # Jargon density
    jargon_count = sum(1 for w in words if w.upper() in JARGON_TERMS)
    jargon_density_pct = round((jargon_count / total_words) * 100, 2)

    # Pronoun ratio
    i_we_count = sum(
        1 for w in words if w.lower() in {"i", "we", "us", "our", "ourselves"}
    )
    you_count = sum(
        1 for w in words if w.lower() in {"you", "your", "yours", "yourself"}
    )
    pronoun_ratio_we_you = round(i_we_count / max(1, you_count), 2)

    # Avg sentence length
    sentences = [s.strip() for s in re.split(r"[.!?]+", corpus) if s.strip()]
    if not sentences:
        avg_sentence_length_words = 0.0
    else:
        avg_sentence_length_words = round(
            sum(len(s.split()) for s in sentences) / len(sentences), 2
        )

    # CTA style
    corpus_lower = corpus.lower()
    imperative_count = sum(corpus_lower.count(p) for p in CTA_IMPERATIVE)
    invitante_count = sum(corpus_lower.count(p) for p in CTA_INVITANTE)
    if imperative_count > invitante_count:
        cta_style = "imperative"
    elif invitante_count > 0:
        cta_style = "invitante"
    else:
        cta_style = "neutral"

    # Exclamation density
    exclamation_count = corpus.count("!")
    exclamation_density_per_100w = round((exclamation_count / total_words) * 100, 2)

    # Bonus: contractions + emoji
    contractions_count = len(CONTRACTIONS.findall(corpus))
    emoji_count = len(EMOJI_REGEX.findall(corpus))

    return {
        "total_words": total_words,
        "jargon_density_pct": jargon_density_pct,
        "pronoun_ratio_we_you": pronoun_ratio_we_you,
        "avg_sentence_length_words": avg_sentence_length_words,
        "cta_style": cta_style,
        "cta_imperative_count": imperative_count,
        "cta_invitante_count": invitante_count,
        "exclamation_density_per_100w": exclamation_density_per_100w,
        "contractions_count": contractions_count,
        "emoji_count": emoji_count,
    }


def score_4dim(metrics: dict, corpus: str) -> dict:
    """Apply rubric to score 1-5 each dim."""
    scores = {}

    # Formal↔Casual (1=Very formal, 5=Very casual)
    casual_signals = 0
    if metrics["contractions_count"] >= 3:
        casual_signals += 1
    if metrics["avg_sentence_length_words"] < 13:
        casual_signals += 1
    if metrics["jargon_density_pct"] < 5:
        casual_signals += 1
    if any(w in corpus.lower().split() for w in CASUAL_LEXICON):
        casual_signals += 1
    formal_casual_score = min(5, max(1, 1 + casual_signals))
    scores["formal_casual"] = {
        "score": formal_casual_score,
        "label": ["Very formal", "Formal", "Neutral", "Casual", "Very casual"][
            formal_casual_score - 1
        ],
        "evidence_metrics": {
            "contractions_count": metrics["contractions_count"],
            "avg_sentence_length_words": metrics["avg_sentence_length_words"],
            "jargon_density_pct": metrics["jargon_density_pct"],
        },
    }

    # Funny↔Serious (1=Very funny, 5=Very serious)
    interjection_count = len(INTERJECTIONS.findall(corpus))
    funny_signals = min(2, interjection_count // 3)  # cap 2 signals
    funny_serious_score = min(5, max(1, 4 - funny_signals))  # default Serious 4
    scores["funny_serious"] = {
        "score": funny_serious_score,
        "label": ["Very funny", "Funny", "Mixed", "Serious", "Very serious"][
            funny_serious_score - 1
        ],
        "evidence_metrics": {"interjection_count": interjection_count},
    }

    # Respectful↔Irreverent (1=Very respectful, 5=Very irreverent)
    provocative_count = sum(corpus.lower().count(w) for w in PROVOCATIVE_LEXICON)
    irreverent_signals = 0
    if metrics["pronoun_ratio_we_you"] > 1.0:
        irreverent_signals += 1
    if provocative_count > 0:
        irreverent_signals += 1
    if metrics["pronoun_ratio_we_you"] > 2.0 or provocative_count > 2:
        irreverent_signals += 1
    respectful_irreverent_score = min(5, max(1, 2 + irreverent_signals))
    scores["respectful_irreverent"] = {
        "score": respectful_irreverent_score,
        "label": [
            "Very respectful",
            "Respectful",
            "Neutral",
            "Irreverent",
            "Very irreverent",
        ][respectful_irreverent_score - 1],
        "evidence_metrics": {
            "pronoun_ratio_we_you": metrics["pronoun_ratio_we_you"],
            "provocative_count": provocative_count,
        },
    }

    # Enthusiastic↔Matter-of-fact (1=Very enthusiastic, 5=Very matter-of-fact)
    enthusiasm_signals = 0
    if metrics["exclamation_density_per_100w"] >= 3:
        enthusiasm_signals += 2
    elif metrics["exclamation_density_per_100w"] >= 1:
        enthusiasm_signals += 1
    if metrics["emoji_count"] > 0:
        enthusiasm_signals += 1
    enthusiastic_matter_of_fact_score = max(1, min(5, 5 - enthusiasm_signals))
    scores["enthusiastic_matter_of_fact"] = {
        "score": enthusiastic_matter_of_fact_score,
        "label": [
            "Very enthusiastic",
            "Enthusiastic",
            "Mixed",
            "Matter-of-fact",
            "Very matter-of-fact",
        ][enthusiastic_matter_of_fact_score - 1],
        "evidence_metrics": {
            "exclamation_density_per_100w": metrics["exclamation_density_per_100w"],
            "emoji_count": metrics["emoji_count"],
        },
    }

    return scores


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute ToV 4-dim NN + derived metrics"
    )
    parser.add_argument("--corpus", required=True, help="Path to corpus text file")
    parser.add_argument(
        "--min-words", type=int, default=200, help="Min words required (default 200)"
    )
    parser.add_argument("--output", help="Output JSON path (default stdout)")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(
            json.dumps({"error": f"corpus not found: {corpus_path}"}), file=sys.stderr
        )
        return 1

    corpus = corpus_path.read_text(encoding="utf-8", errors="ignore")
    metrics = compute_metrics(corpus)

    if metrics.get("error") or metrics["total_words"] < args.min_words:
        result = {
            "insufficient_evidence": True,
            "reason": f"corpus too small ({metrics.get('total_words', 0)} words, min {args.min_words} required)",
            "suggestion": "Espandi corpus con: about page + 5 latest blog posts + LinkedIn About",
            "corpus_size_words": metrics.get("total_words", 0),
        }
    else:
        scores = score_4dim(metrics, corpus)
        labels = [
            scores[d]["label"]
            for d in [
                "formal_casual",
                "funny_serious",
                "respectful_irreverent",
                "enthusiastic_matter_of_fact",
            ]
        ]
        result = {
            "insufficient_evidence": False,
            "corpus_size_words": metrics["total_words"],
            "scores": scores,
            "derived_metrics": metrics,
            "tov_summary_label": " + ".join(labels),
        }

    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        log.info(f"ToV scored to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
