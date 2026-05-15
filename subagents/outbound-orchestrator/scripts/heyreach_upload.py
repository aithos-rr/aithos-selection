#!/usr/bin/env python3
"""
heyreach_upload.py — Upload sequence JSON portable to HeyReach via MCP/API

Usage:
    python heyreach_upload.py --sequence-json output/sequence_<...>.json \\
        --campaign-name "Yellow Tech LinkedIn Q2 2026" [--list-id <ID>] \\
        [--linkedin-account-ids 186644] [--dry-run] [--confirm]

Default: --dry-run. Use --no-dry-run + --confirm to execute.

CRITICAL: HeyReach uses SINGLE-brace placeholder {first_name}, NOT double-brace.
This script ENFORCES single-brace + auto-fixes any {{var}} found in input.

Reference: ~/.claude/skills/heyreach-api/SKILL.md (testato 27/04/2026).
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

DOUBLE_BRACE = re.compile(r"\{\{([A-Za-z][A-Za-z0-9_-]*)\}\}")


def fix_double_brace(s):
    """Auto-fix {{var}} → {var} for HeyReach. CRITICAL — vedi skill heyreach-api."""
    if not isinstance(s, str):
        return s
    return DOUBLE_BRACE.sub(r"{\1}", s)


def recursive_fix_double_brace(obj):
    """Recursively fix double-brace in any nested structure."""
    if isinstance(obj, str):
        return fix_double_brace(obj)
    elif isinstance(obj, dict):
        return {k: recursive_fix_double_brace(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_fix_double_brace(item) for item in obj]
    return obj


def build_sequence_tree(linkedin_steps):
    """Build HeyReach recursive sequence tree from flat step list.

    HeyReach sequence shape (recursive tree):
    - nodeType: CONNECTION_REQUEST | MESSAGE | CHECK_IS_CONNECTION | INMAIL | END
    - actionDelay + actionDelayUnit
    - payload: {messages: [...], fallbackMessage: "..."}
    - conditionalNode: child if condition true (e.g. is_connection_accepted)
    - unconditionalNode: child default
    """
    if not linkedin_steps:
        return {"nodeType": "END"}

    # Sort by step_n
    steps_sorted = sorted(linkedin_steps, key=lambda s: s.get("step_n", 0))

    # Build linear chain (most common pattern)
    # First step: CONNECTION_REQUEST or MESSAGE
    root = build_node(steps_sorted[0], steps_sorted[1:])
    return root


def build_node(step, remaining_steps):
    """Recursively build node + children."""
    node_type = step.get("node_type", "MESSAGE")

    node = {
        "nodeType": node_type,
        "actionDelay": step.get("delay_days", 0),
        "actionDelayUnit": "DAYS",
        "payload": {
            "messages": [fix_double_brace(m) for m in step.get("messages", [])],
            "fallbackMessage": fix_double_brace(step.get("fallback_message", "")),
        },
    }

    # If conditional (e.g. CONNECTION_REQUEST → CHECK_IS_CONNECTION → MESSAGE)
    if node_type == "CONNECTION_REQUEST" and remaining_steps:
        # Wrap next step under CHECK_IS_CONNECTION
        check_node = {
            "nodeType": "CHECK_IS_CONNECTION",
            "actionDelay": remaining_steps[0].get("delay_days", 5),
            "actionDelayUnit": "DAYS",
            "conditionalNode": build_node(remaining_steps[0], remaining_steps[1:]),
            "unconditionalNode": {"nodeType": "END"},
        }
        node["conditionalNode"] = check_node
        node["unconditionalNode"] = {"nodeType": "END"}
    elif remaining_steps:
        # Linear continuation
        node["unconditionalNode"] = build_node(remaining_steps[0], remaining_steps[1:])
    else:
        node["unconditionalNode"] = {"nodeType": "END"}

    return node


def translate_lead_for_heyreach(lead):
    """Convert lead to HeyReach format with customFields array."""
    custom_fields = lead.get("custom_fields", {})

    # HeyReach customFields = list of {name, value} (NOT dict)
    custom_fields_array = [
        {"name": k, "value": fix_double_brace(str(v))} for k, v in custom_fields.items()
    ]

    return {
        "linkedInUrl": lead.get("linkedin_url", ""),
        "firstName": lead.get("first_name", ""),
        "lastName": lead.get("last_name", ""),
        "company": lead.get("company", ""),
        "customFields": custom_fields_array,
    }


def build_api_plan(sequence_json, campaign_name, list_id, linkedin_account_ids):
    """Build ordered MCP/API call plan."""
    linkedin_steps = [
        s for s in sequence_json["steps"] if s.get("channel") == "linkedin"
    ]

    if not linkedin_steps:
        print("⚠️  No LinkedIn steps found. Skipping HeyReach upload.", file=sys.stderr)
        return None

    leads_heyreach = [
        translate_lead_for_heyreach(lead) for lead in sequence_json["leads"]
    ]

    sequence_tree = build_sequence_tree(linkedin_steps)
    sequence_tree_fixed = recursive_fix_double_brace(sequence_tree)  # Belt & suspenders

    plan = {
        "execution_order": [
            {
                "step": 1,
                "tool": "mcp__heyreach__create_empty_list"
                if list_id is None
                else "noop",
                "args": {"name": f"{campaign_name} — leads"} if list_id is None else {},
                "note": "Skip if list_id provided",
            },
            {
                "step": 2,
                "tool": "mcp__heyreach__add_leads_to_list_v2",
                "args": {
                    "listId": list_id or "<list_id_from_step_1>",
                    "leads": leads_heyreach,
                },
            },
            {
                "step": 3,
                "tool": "<API direct>",
                "endpoint": "POST https://api.heyreach.io/api/public/campaign/Create",
                "headers": {"X-API-KEY": "<HEYREACH_API_KEY env>"},
                "body": {
                    "name": campaign_name,
                    "linkedInAccountIds": linkedin_account_ids or [],
                    "linkedInUserListId": list_id or "<list_id_from_step_1>",
                },
                "note": "Returns {campaignId: <new_id>}, status DRAFT",
            },
            {
                "step": 4,
                "tool": "<API direct>",
                "endpoint": "POST https://api.heyreach.io/api/public/campaign/UpdateSequence",
                "headers": {"X-API-KEY": "<HEYREACH_API_KEY env>"},
                "body": {
                    "campaignId": "<campaign_id_from_step_3>",
                    "sequence": sequence_tree_fixed,
                },
                "note": "Single-brace placeholder enforced. Auto-fix applied to all messages.",
            },
            {
                "step": 5,
                "tool": "mcp__heyreach__resume_campaign",
                "args": {"campaignId": "<campaign_id_from_step_3>"},
                "note": "EXECUTES the campaign — only call if --confirm",
            },
        ],
        "summary": {
            "campaign_name": campaign_name,
            "linkedin_steps_count": len(linkedin_steps),
            "leads_count": len(leads_heyreach),
            "linkedin_account_ids": linkedin_account_ids,
            "list_id": list_id,
            "double_brace_fixes_applied": True,
        },
    }

    return plan


def main():
    parser = argparse.ArgumentParser(
        description="HeyReach LinkedIn campaign upload from sequence JSON"
    )
    parser.add_argument(
        "--sequence-json", required=True, help="Path to sequence JSON portable"
    )
    parser.add_argument("--campaign-name", required=True)
    parser.add_argument("--list-id", type=int, help="Existing list_id (skip create)")
    parser.add_argument(
        "--linkedin-account-ids",
        type=int,
        nargs="+",
        help="LinkedIn sender account IDs",
    )
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    seq_path = Path(args.sequence_json)
    if not seq_path.exists():
        print(f"❌ Sequence JSON not found: {seq_path}", file=sys.stderr)
        sys.exit(1)

    with open(seq_path) as f:
        sequence_json = json.load(f)

    # Build plan
    plan = build_api_plan(
        sequence_json, args.campaign_name, args.list_id, args.linkedin_account_ids
    )

    if plan is None:
        print(
            "ℹ️  No LinkedIn steps in sequence. Skipping HeyReach upload (email-only campaign)."
        )
        sys.exit(0)

    # API key check (only if not dry-run)
    if not args.dry_run:
        if not os.environ.get("HEYREACH_API_KEY"):
            print("❌ HEYREACH_API_KEY env var missing.", file=sys.stderr)
            print(
                "Add to ~/.zshrc: export HEYREACH_API_KEY='your_key'", file=sys.stderr
            )
            sys.exit(1)
        if not args.confirm:
            print("⚠️  --no-dry-run requires --confirm flag. Aborting.", file=sys.stderr)
            sys.exit(1)
        if not args.linkedin_account_ids:
            print("❌ --linkedin-account-ids required for execute.", file=sys.stderr)
            sys.exit(1)

    # Save plan
    Path(args.output_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    plan_path = Path(args.output_dir) / f"heyreach_upload_plan_{ts}.json"
    with open(plan_path, "w") as f:
        json.dump(
            {
                "dry_run": args.dry_run,
                "confirm": args.confirm,
                "created_at": datetime.now().isoformat(),
                "plan": plan,
            },
            f,
            indent=2,
        )

    print(f"📋 HeyReach upload plan generated: {plan_path}")
    print(f"\nSummary:")
    print(f"  Campaign: {plan['summary']['campaign_name']}")
    print(f"  LinkedIn steps: {plan['summary']['linkedin_steps_count']}")
    print(f"  Leads: {plan['summary']['leads_count']}")
    print(f"  Single-brace enforcement: ✓ applied")

    if args.dry_run:
        print(f"\n🔍 DRY-RUN mode — no API call made.")
    else:
        print(f"\n🚀 Ready to execute via subagent MCP/API calls.")


if __name__ == "__main__":
    main()
