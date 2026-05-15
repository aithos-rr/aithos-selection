#!/usr/bin/env python3
"""Costruisce gap-matrix.json + gap-narrative.md da positioning/tov/reviews JSON + cliente baseline.

Usage: python scripts/gap_matrix_build.py --baseline-from-config [--positioning-glob "output/positioning_*.json"] [--tov-glob "output/tov_*.json"] [--reviews-glob "output/reviews_*.json"] [--output-matrix output/gap-matrix.json] [--output-narrative output/gap-narrative.md]
Author: Filippo Greco / competitor-deep-dive 2026
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        json.dumps(
            {
                "error": "PyYAML not installed. Run: pip install -r scripts/requirements.txt"
            }
        ),
        file=sys.stderr,
    )
    sys.exit(2)

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = ".claude/agents/competitor-deep-dive/memory/config.md"

REQUIRED_BASELINE_FIELDS = ["tagline", "value_prop", "icp"]


def load_config_baseline(config_path: Path) -> dict:
    """Extract business.baseline from config.md YAML body."""
    if not config_path.exists():
        return {"error": f"config not found: {config_path}"}
    content = config_path.read_text(encoding="utf-8")
    if "---" in content:
        body = content.split("---", 2)[-1].strip()
    else:
        body = content
    try:
        config = yaml.safe_load(body) or {}
    except yaml.YAMLError as e:
        return {"error": f"YAML parse error: {e}"}
    baseline = (config.get("business") or {}).get("baseline", {})
    return baseline


def validate_baseline(baseline: dict) -> dict:
    """Block if any of tagline/value_prop/icp missing."""
    missing = [
        f
        for f in REQUIRED_BASELINE_FIELDS
        if not baseline.get(f) or str(baseline.get(f)).strip() == ""
    ]
    if missing:
        return {
            "valid": False,
            "missing": missing,
            "error": f"Baseline mancante: {missing}. Definisci tutti 3 campi prima di procedere - gap analysis senza baseline e fake-news.",
        }
    return {"valid": True, "baseline": baseline}


def load_artifacts(positioning_glob: str, tov_glob: str, reviews_glob: str) -> dict:
    """Load all positioning/tov/reviews JSON, group by competitor slug."""
    competitors: dict = {}

    for f in glob.glob(positioning_glob):
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            slug = Path(f).stem.replace("positioning_", "")
            competitors.setdefault(slug, {})["positioning"] = data
        except (json.JSONDecodeError, OSError) as e:
            log.warning(f"Skip {f}: {e}")

    for f in glob.glob(tov_glob):
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            slug = Path(f).stem.replace("tov_", "")
            competitors.setdefault(slug, {})["tov"] = data
        except (json.JSONDecodeError, OSError):
            pass

    for f in glob.glob(reviews_glob):
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            slug = Path(f).stem.replace("reviews_", "")
            competitors.setdefault(slug, {})["reviews"] = data
        except (json.JSONDecodeError, OSError):
            pass

    return competitors


def compute_gap_score(
    impact: int, ease: int, evidence_strength: int, complexity_penalty: int
) -> float:
    """Apply ranking formula (DECISION-005 candidate)."""
    return round((impact * ease * evidence_strength) / max(1, complexity_penalty), 2)


def categorize_gap(gap: dict) -> str:
    """Categorize gap based on impact + ease + evidence."""
    impact = gap["impact"]
    ease = gap["ease"]
    evidence = gap["evidence_strength"]

    if impact <= 2 or evidence <= 2:
        return "ignore"
    if impact >= 3 and ease >= 4:
        return "quick_win"
    if impact >= 4 and ease <= 3:
        return "strategic_bet"
    if impact >= 3 and 2 <= ease <= 3:
        return "backlog"
    return "backlog"


def build_template_gaps(competitors: dict, baseline: dict) -> list:
    """Build a template list of common gap candidates.

    Note: questa e una BASELINE template. Il subagent rifinira i score
    impact/ease/evidence_strength/complexity_penalty basandosi su evidence reali.
    """
    gaps = []
    n_comp = len(competitors)

    gaps.append(
        {
            "id": "gap-001",
            "dimension": "feature",
            "title": "AI-assisted core capability",
            "description": f"Universal want emerso da reviews customer cross-{n_comp} competitor",
            "impact": 5,
            "ease": 3,
            "evidence_strength": 4,
            "complexity_penalty": 2,
            "love_hate_want": "want",
            "category_template": "strategic_bet",
        }
    )

    gaps.append(
        {
            "id": "gap-002",
            "dimension": "segment",
            "title": "Enterprise SOC2 + RBAC",
            "description": "Compliance gap se cliente non ha SOC2 + competitor si",
            "impact": 4,
            "ease": 2,
            "evidence_strength": 3,
            "complexity_penalty": 3,
            "love_hate_want": "love",
            "category_template": "strategic_bet",
        }
    )

    gaps.append(
        {
            "id": "gap-003",
            "dimension": "pricing",
            "title": "Pricing transparency public",
            "description": "Quick win se cliente ha call-only e competitor public",
            "impact": 3,
            "ease": 5,
            "evidence_strength": 4,
            "complexity_penalty": 1,
            "love_hate_want": "hate",
            "category_template": "quick_win",
        }
    )

    gaps.append(
        {
            "id": "gap-004",
            "dimension": "tov",
            "title": "ToV differentiation (blue ocean)",
            "description": "Se tutti competitor convergono su ToV X, pivot su Y",
            "impact": 4,
            "ease": 4,
            "evidence_strength": 3,
            "complexity_penalty": 1,
            "love_hate_want": "n/a",
            "category_template": "quick_win",
        }
    )

    gaps.append(
        {
            "id": "gap-005",
            "dimension": "format",
            "title": "Format gap (es. podcast / video)",
            "description": "Se nessun competitor ha format X, opportunita content",
            "impact": 3,
            "ease": 4,
            "evidence_strength": 3,
            "complexity_penalty": 1,
            "love_hate_want": "n/a",
            "category_template": "quick_win",
        }
    )

    for gap in gaps:
        gap["gap_score"] = compute_gap_score(
            gap["impact"],
            gap["ease"],
            gap["evidence_strength"],
            gap["complexity_penalty"],
        )
        gap["category"] = categorize_gap(gap)

    return gaps


def render_narrative(gaps: list, baseline: dict, competitors: dict) -> str:
    """Render gap-narrative.md."""
    sorted_gaps = sorted(gaps, key=lambda g: g["gap_score"], reverse=True)
    quick_wins = [g for g in sorted_gaps if g["category"] == "quick_win"]
    strategic_bets = [g for g in sorted_gaps if g["category"] == "strategic_bet"]
    backlog = [g for g in sorted_gaps if g["category"] == "backlog"]
    ignored = [g for g in sorted_gaps if g["category"] == "ignore"]

    md = [
        "# Gap Analysis - narrative",
        "",
        f"> Cliente baseline: **{baseline.get('tagline')}**",
        f"> Value prop: {baseline.get('value_prop')}",
        f"> ICP: {baseline.get('icp')}",
        f"> Competitor analizzati: {', '.join(competitors.keys()) if competitors else '(nessuno - template mode)'}",
        "",
        "## Quick wins (impact >=3 + ease >=4)",
        "",
    ]
    for i, g in enumerate(quick_wins, 1):
        md.append(f"### {i}. {g['title']}")
        md.append(
            f"- **Score**: {g['gap_score']} (impact {g['impact']} x ease {g['ease']} x evidence {g['evidence_strength']} / {g['complexity_penalty']})"
        )
        md.append(f"- **Cosa**: {g['description']}")
        md.append(f"- **Dim**: {g['dimension']}")
        md.append("")

    md.append("## Strategic bets (impact >=4 + ease <=3)")
    md.append("")
    for i, g in enumerate(strategic_bets, 1):
        md.append(f"### {i}. {g['title']}")
        md.append(f"- **Score**: {g['gap_score']}")
        md.append(f"- **Cosa**: {g['description']}")
        md.append("")

    if backlog:
        md.append("## Backlog (impact >=3 + ease 2-3)")
        md.append("")
        for g in backlog:
            md.append(f"- {g['title']} - score {g['gap_score']}")
        md.append("")

    if ignored:
        md.append("## Ignore (low impact / low evidence)")
        md.append("")
        for g in ignored:
            md.append(
                f"- {g['title']} - score {g['gap_score']} (motivo: low impact OR low evidence)"
            )
        md.append("")

    return "\n".join(md)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build gap matrix + narrative per /competitor-deep-dive"
    )
    parser.add_argument(
        "--baseline-from-config",
        action="store_true",
        help="Load baseline from <memory>/config.md",
    )
    parser.add_argument(
        "--config-path",
        default=DEFAULT_CONFIG_PATH,
        help=f"Config path (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--positioning-glob",
        default="output/positioning_*.json",
        help="Glob pattern positioning files",
    )
    parser.add_argument(
        "--tov-glob", default="output/tov_*.json", help="Glob tov files"
    )
    parser.add_argument(
        "--reviews-glob", default="output/reviews_*.json", help="Glob reviews files"
    )
    parser.add_argument(
        "--output-matrix",
        default="output/gap-matrix.json",
        help="Output gap-matrix.json path",
    )
    parser.add_argument(
        "--output-narrative",
        default="output/gap-narrative.md",
        help="Output gap-narrative.md path",
    )
    args = parser.parse_args()

    if args.baseline_from_config:
        baseline = load_config_baseline(Path(args.config_path).expanduser())
        if "error" in baseline:
            print(json.dumps(baseline, indent=2), file=sys.stderr)
            return 1
    else:
        print(
            json.dumps(
                {"error": "--baseline-from-config required (or pass baseline JSON)"}
            ),
            file=sys.stderr,
        )
        return 1

    validation = validate_baseline(baseline)
    if not validation["valid"]:
        print(json.dumps(validation, indent=2), file=sys.stderr)
        return 1

    competitors = load_artifacts(
        args.positioning_glob, args.tov_glob, args.reviews_glob
    )
    if not competitors:
        log.warning("no artifacts found — running gap-matrix in template mode")

    gaps = build_template_gaps(competitors, baseline)

    matrix = {
        "client_baseline": baseline,
        "competitors_analyzed": list(competitors.keys()),
        "framework_used_template": ["Strategy Canvas", "JTBD", "Feature Matrix"],
        "gaps": gaps,
        "ranking": [
            g["id"] for g in sorted(gaps, key=lambda g: g["gap_score"], reverse=True)
        ],
        "categorized": {
            "quick_wins": [g["id"] for g in gaps if g["category"] == "quick_win"],
            "strategic_bets": [
                g["id"] for g in gaps if g["category"] == "strategic_bet"
            ],
            "backlog": [g["id"] for g in gaps if g["category"] == "backlog"],
            "ignore": [g["id"] for g in gaps if g["category"] == "ignore"],
        },
        "_note": "TEMPLATE - subagent must refine score components with real evidence from JSON artifacts before final render",
    }

    Path(args.output_matrix).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_matrix).write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    log.info(f"Matrix written to {args.output_matrix}")

    narrative = render_narrative(gaps, baseline, competitors)
    Path(args.output_narrative).write_text(narrative, encoding="utf-8")
    log.info(f"Narrative written to {args.output_narrative}")

    print(
        json.dumps(
            {
                "ok": True,
                "matrix_path": args.output_matrix,
                "narrative_path": args.output_narrative,
                "gaps_count": len(gaps),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
