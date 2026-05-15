#!/usr/bin/env python3
"""
validate_input.py — Validate `/lead-finder-pro` CSV output schema (17 colonne)

Usage:
    python validate_input.py --csv <path> [--filter-grade A,B] [--reject-personal-email]

Input contract (output `/lead-finder-pro`):
    name, company, email, email_confidence, email_verified_at, linkedin, role,
    role_confidence, company_size, industry, intent_signals, score, grade,
    score_breakdown, _conflicts, _enriched_at, gdpr_status (optional if EU), notes

Output:
    - Print summary stats
    - Reject input + exit 1 if schema not compliant
    - Save validated subset to `output/leads_validated_<ts>.json`
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Schema mandatory columns (subset of 17)
REQUIRED_COLUMNS = ["name", "company", "email", "email_confidence", "score", "grade"]

# Filter defaults
DEFAULT_GRADE_FILTER = ["A", "B"]
DEFAULT_EMAIL_CONFIDENCE_MIN = 0.80

# Role-based email prefixes (rejected by default)
ROLE_BASED_PREFIXES = {
    "info",
    "sales",
    "support",
    "noreply",
    "admin",
    "contact",
    "hello",
    "team",
    "office",
    "hr",
    "marketing",
    "legal",
    "billing",
}

# Personal email domains (rejected if --reject-personal-email)
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "yahoo.com",
    "yahoo.it",
    "yahoo.co.uk",
    "hotmail.com",
    "hotmail.it",
    "outlook.com",
    "live.com",
    "msn.com",
    "icloud.com",
    "me.com",
    "mac.com",
    "libero.it",
    "alice.it",
    "tin.it",
    "virgilio.it",
    "tiscali.it",
    "fastwebnet.it",
    "aol.com",
    "protonmail.com",
    "tutanota.com",
    "orange.fr",
    "wanadoo.fr",
    "free.fr",
    "web.de",
    "gmx.de",
    "t-online.de",
}


def is_role_based(email):
    if "@" not in email:
        return False
    local = email.split("@")[0].lower().strip()
    return local in ROLE_BASED_PREFIXES


def is_personal_email(email):
    if "@" not in email:
        return False
    domain = email.split("@")[1].lower().strip()
    return domain in PERSONAL_EMAIL_DOMAINS


def validate_schema(rows, required_cols):
    """Return (is_valid, missing_cols)."""
    if not rows:
        return False, ["__empty_csv"]
    actual_cols = set(rows[0].keys())
    missing = [c for c in required_cols if c not in actual_cols]
    return len(missing) == 0, missing


def filter_leads(rows, grade_filter, conf_min, reject_role_based, reject_personal):
    """Apply filters, return (compliant, excluded_with_reason)."""
    compliant = []
    excluded = []
    for row in rows:
        # Schema field check (cell-level)
        if not row.get("email") or not row.get("name") or not row.get("company"):
            excluded.append({"row": row, "reason": "missing_required_field"})
            continue

        # Grade filter
        grade = (row.get("grade") or "").strip().upper()
        if grade not in grade_filter:
            excluded.append({"row": row, "reason": f"grade_not_in_filter ({grade})"})
            continue

        # Email confidence
        try:
            conf = float(row.get("email_confidence", 0))
        except (ValueError, TypeError):
            conf = 0.0
        if conf < conf_min:
            excluded.append(
                {"row": row, "reason": f"email_confidence_low ({conf:.2f})"}
            )
            continue

        # GDPR status
        gdpr = (row.get("gdpr_status") or "").strip().lower()
        if gdpr == "excluded":
            excluded.append({"row": row, "reason": "gdpr_excluded"})
            continue

        # Role-based email
        email = row["email"].strip()
        if reject_role_based and is_role_based(email):
            excluded.append({"row": row, "reason": "role_based_email"})
            continue

        # Personal email
        if reject_personal and is_personal_email(email):
            excluded.append(
                {"row": row, "reason": f"personal_email ({email.split('@')[1]})"}
            )
            continue

        compliant.append(row)

    return compliant, excluded


def main():
    parser = argparse.ArgumentParser(
        description="Validate /lead-finder-pro CSV output schema"
    )
    parser.add_argument("--csv", required=True, help="Path to CSV input")
    parser.add_argument(
        "--filter-grade",
        default="A,B",
        help="Grade filter, comma-separated (default: A,B)",
    )
    parser.add_argument(
        "--email-confidence-min", type=float, default=DEFAULT_EMAIL_CONFIDENCE_MIN
    )
    parser.add_argument("--reject-personal-email", action="store_true", default=True)
    parser.add_argument(
        "--no-reject-role-based",
        dest="reject_role_based",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--output-dir", default="output", help="Where to save validated leads JSON"
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    grade_filter = [g.strip().upper() for g in args.filter_grade.split(",")]

    # Read CSV
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Schema validation
    is_valid, missing = validate_schema(rows, REQUIRED_COLUMNS)
    if not is_valid:
        print(
            f"❌ Schema not conforme /lead-finder-pro output (17 colonne).",
            file=sys.stderr,
        )
        print(f"   Missing required columns: {missing}", file=sys.stderr)
        print(f"   Expected: {REQUIRED_COLUMNS}", file=sys.stderr)
        print(
            f"   Actual: {list(rows[0].keys()) if rows else '(empty CSV)'}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"✓ Schema valid. {len(rows)} rows.")

    # Filter
    compliant, excluded = filter_leads(
        rows,
        grade_filter,
        args.email_confidence_min,
        args.reject_role_based,
        args.reject_personal_email,
    )

    # Summary
    print(f"\n📊 Validation summary:")
    print(f"   Total input: {len(rows)}")
    print(f"   Compliant: {len(compliant)}")
    print(f"   Excluded: {len(excluded)}")

    breakdown = {}
    for ex in excluded:
        reason = ex["reason"].split(" ")[0]
        breakdown[reason] = breakdown.get(reason, 0) + 1
    for reason, count in sorted(breakdown.items(), key=lambda x: -x[1]):
        print(f"     - {reason}: {count}")

    # Save validated
    os.makedirs(args.output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = Path(args.output_dir) / f"leads_validated_{ts}.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "validated_at": datetime.now().isoformat(),
                "source_csv": str(csv_path),
                "filters_applied": {
                    "grade": grade_filter,
                    "email_confidence_min": args.email_confidence_min,
                    "reject_role_based": args.reject_role_based,
                    "reject_personal_email": args.reject_personal_email,
                },
                "summary": {
                    "total_input": len(rows),
                    "compliant_count": len(compliant),
                    "excluded_count": len(excluded),
                },
                "compliant_leads": compliant,
                "excluded_breakdown": breakdown,
            },
            f,
            indent=2,
            default=str,
        )

    print(f"\n✅ Saved: {output_path}")
    if not compliant:
        print("⚠️  Zero compliant leads dopo filter. Check criteria.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
