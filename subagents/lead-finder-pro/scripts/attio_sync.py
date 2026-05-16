#!/usr/bin/env python3
"""Genera payload sync Hot leads -> Attio CRM via attio-mcp.

NB: questo script NON chiama Attio API direttamente. Genera payload structured che
il subagent passa a mcp__attio__create_record / update_record / search_records.
Per dedup: produce anche search payload da chiamare prima di create.

Usage:
  python scripts/attio_sync.py --input-json leads.json --filter-grade "A,B" --dry-run
  python scripts/attio_sync.py --input-json leads.json --object-slug people --dedup-by email

Author: Filippo Greco / lead-finder-pro 2026
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
log = logging.getLogger(__name__)


def load_leads(path: Path) -> list[dict]:
    """Load JSON list of leads (or dict with 'leads' key)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "leads" in data:
        return data["leads"]
    if isinstance(data, list):
        return data
    raise ValueError("Input JSON must be list[lead] or dict with 'leads' key")


def lead_to_attio_payload(lead: dict, object_slug: str) -> dict:
    """Map lead JSON to Attio record payload structure."""
    values = {
        "name": [
            {
                "first_name": (lead.get("name") or "").split(" ", 1)[0],
                "last_name": " ".join((lead.get("name") or "").split(" ")[1:]),
            }
        ],
        "email_addresses": [{"email_address": lead["email"]}]
        if lead.get("email")
        else [],
        "company": [
            {"target_object": "companies", "target_record_id": lead.get("company")}
        ]
        if lead.get("company")
        else [],
        "job_title": lead.get("role"),
    }
    linkedin = lead.get("linkedin")
    if linkedin:
        values["linkedin"] = [{"url": linkedin}]

    score = lead.get("score")
    grade = lead.get("grade")
    if score is not None:
        values["lead_score"] = score
    if grade:
        values["lead_grade"] = grade

    return {
        "object_slug": object_slug,
        "values": {k: v for k, v in values.items() if v not in (None, [], "")},
    }


def search_payload_for_dedup(lead: dict, object_slug: str, dedup_by: str) -> dict:
    """Build search query for dedup check."""
    if dedup_by == "email":
        return {
            "object_slug": object_slug,
            "filter": {"email_addresses": {"email_address": lead.get("email")}},
            "_mcp_call": "mcp__attio__search_records",
        }
    if dedup_by == "linkedin":
        return {
            "object_slug": object_slug,
            "filter": {"linkedin": {"url": lead.get("linkedin")}},
            "_mcp_call": "mcp__attio__search_records",
        }
    return {
        "object_slug": object_slug,
        "filter": {dedup_by: lead.get(dedup_by)},
        "_mcp_call": "mcp__attio__search_records",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate attio-mcp sync payload")
    parser.add_argument("--input-json", required=True, help="Lead enriched JSON list")
    parser.add_argument(
        "--object-slug", default="people", help="Attio object slug (default: people)"
    )
    parser.add_argument(
        "--dedup-by", default="email", help="Field to dedup by (default: email)"
    )
    parser.add_argument(
        "--filter-grade",
        default="A,B",
        help="Comma-separated grades to sync (default: A,B)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without creating final payloads",
    )
    args = parser.parse_args()

    input_path = Path(args.input_json).expanduser()
    if not input_path.exists():
        print(json.dumps({"error": f"Input not found: {input_path}"}), file=sys.stderr)
        return 1

    leads = load_leads(input_path)
    grades_filter = {g.strip() for g in args.filter_grade.split(",")}

    to_create = []
    to_update = []
    to_skip = []

    for lead in leads:
        grade = lead.get("grade")
        if grade not in grades_filter:
            to_skip.append(
                {
                    "lead_id": lead.get("lead_id") or lead.get("name"),
                    "reason": f"grade {grade} excluded",
                }
            )
            continue

        if not lead.get("email") and args.dedup_by == "email":
            to_skip.append(
                {"lead_id": lead.get("name"), "reason": "no email for dedup"}
            )
            continue

        search = search_payload_for_dedup(lead, args.object_slug, args.dedup_by)
        record_payload = lead_to_attio_payload(lead, args.object_slug)

        item = {
            "lead": {
                "name": lead.get("name"),
                "email": lead.get("email"),
                "grade": grade,
                "score": lead.get("score"),
            },
            "search_first": search,
            "create_payload": {
                **record_payload,
                "_mcp_call": "mcp__attio__create_record",
                "_note": "Call this only if search_first returns 0 matches.",
            },
            "update_payload": {
                **record_payload,
                "_mcp_call": "mcp__attio__update_record",
                "_note": "Call this only if search_first returns exactly 1 match. Pass record_id from search.",
            },
        }

        if args.dry_run:
            log.info(f"DRY-RUN would sync: {lead.get('name')} ({grade})")
        to_create.append(item)

    output = {
        "summary": {
            "total_input": len(leads),
            "to_sync": len(to_create),
            "skipped": len(to_skip),
            "filter_grade": list(grades_filter),
            "dedup_by": args.dedup_by,
            "dry_run": args.dry_run,
        },
        "to_sync": to_create,
        "to_skip": to_skip,
    }

    print(json.dumps(output, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
