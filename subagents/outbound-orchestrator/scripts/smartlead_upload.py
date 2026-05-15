#!/usr/bin/env python3
"""
smartlead_upload.py — Upload sequence JSON portable to SmartLead via MCP/API

Usage:
    python smartlead_upload.py --sequence-json output/sequence_<...>.json \\
        --campaign-name "Yellow Tech Q2 2026" [--dry-run] [--confirm]

Default: --dry-run (NO API call). Use --no-dry-run + --confirm to execute reale.

This script PRINTS the API call sequence for the subagent to execute via MCP tools.
Subagent reads output, executes mcp__smartlead__* tools accordingly.

Logic flow:
1. Load sequence JSON portable (output of sequence-builder)
2. Validate structure
3. Translate placeholder single-brace → SmartLead double-brace `{{var}}`
4. Output API call plan (JSON):
   - mcp__smartlead__smartlead_create_campaign
   - mcp__smartlead__smartlead_save_campaign_sequence
   - mcp__smartlead__smartlead_add_email_account_to_campaign
   - mcp__smartlead__smartlead_add_leads_to_campaign
   - mcp__smartlead__smartlead_update_campaign_schedule
   - mcp__smartlead__smartlead_update_campaign_status (START se --confirm)

If --dry-run: stop after step 4 plan, NO API call.
If --confirm: execute via MCP (subagent layer).
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def to_smartlead_placeholder(text):
    """Convert single-brace {var} to SmartLead double-brace {{var}}.

    SmartLead uses {{first_name}}, {{company}}, etc.
    HeyReach uses {first_name}, {company}.
    Sequence JSON portable schema uses single-brace by default.
    """
    if not isinstance(text, str):
        return text
    # Match {var} not already inside {{...}} — careful regex
    # Pattern: {word} not preceded by { and not followed by }
    pattern = re.compile(r"(?<!\{)\{([A-Za-z][A-Za-z0-9_-]*)\}(?!\})")
    return pattern.sub(r"{{\1}}", text)


def translate_step_for_smartlead(step):
    """Convert step from portable schema to SmartLead API payload."""
    if step["channel"] != "email":
        # Skip LinkedIn steps for SmartLead
        return None

    return {
        "seq_number": step["step_n"],
        "seq_delay_days": step["delay_days"],
        "subject": to_smartlead_placeholder(step["subject_variants"][0]),
        "email_body": to_smartlead_placeholder(step["body_variants"][0]),
        # If A/B test: SmartLead supports `subject_variant_2` + `email_body_variant_2`
        "subject_variant_2": to_smartlead_placeholder(step["subject_variants"][1])
        if len(step.get("subject_variants", [])) > 1
        else None,
        "email_body_variant_2": to_smartlead_placeholder(step["body_variants"][1])
        if len(step.get("body_variants", [])) > 1
        else None,
        "send_as_new_thread": False,
    }


def translate_lead_for_smartlead(lead):
    """Convert lead to SmartLead format."""
    custom_fields = lead.get("custom_fields", {})
    # SmartLead expects flat custom_fields object
    return {
        "first_name": lead.get("first_name", ""),
        "last_name": lead.get("last_name", ""),
        "email": lead.get("email", ""),
        "company_name": lead.get("company", ""),
        "phone_number": lead.get("phone", ""),
        "linkedin_profile": lead.get("linkedin_url", ""),
        "custom_fields": {
            k: v
            for k, v in custom_fields.items()
            # Drop LinkedIn-specific fields
            if not k.startswith("li_")
        },
    }


def build_api_plan(sequence_json, campaign_name):
    """Build ordered MCP call plan."""
    email_steps = []
    for step in sequence_json["steps"]:
        translated = translate_step_for_smartlead(step)
        if translated:
            email_steps.append(translated)

    leads_smartlead = [
        translate_lead_for_smartlead(lead) for lead in sequence_json["leads"]
    ]

    plan = {
        "execution_order": [
            {
                "step": 1,
                "tool": "mcp__smartlead__smartlead_create_campaign",
                "args": {"name": campaign_name, "client_id": None},
            },
            {
                "step": 2,
                "tool": "mcp__smartlead__smartlead_save_campaign_sequence",
                "args": {
                    "campaign_id": "<campaign_id_from_step_1>",
                    "sequences": email_steps,
                },
            },
            {
                "step": 3,
                "tool": "mcp__smartlead__smartlead_add_email_account_to_campaign",
                "args": {
                    "campaign_id": "<campaign_id_from_step_1>",
                    "email_account_ids": "<USER_PROVIDES>",
                },
                "note": "Subagent should ask user which mailbox(es) to use",
            },
            {
                "step": 4,
                "tool": "mcp__smartlead__smartlead_add_leads_to_campaign",
                "args": {
                    "campaign_id": "<campaign_id_from_step_1>",
                    "lead_list": leads_smartlead,
                    "settings": {
                        "ignore_global_block_list": False,
                        "ignore_unsubscribe_list": False,
                        "ignore_duplicate_leads_in_other_campaigns": False,
                    },
                },
            },
            {
                "step": 5,
                "tool": "mcp__smartlead__smartlead_update_campaign_schedule",
                "args": {
                    "campaign_id": "<campaign_id_from_step_1>",
                    "timezone": "Europe/Rome",
                    "days_of_the_week": [2, 3, 4],  # Tue-Thu (default)
                    "start_hour": "09:00",
                    "end_hour": "13:00",
                    "min_time_btw_emails": 10,
                    "max_new_leads_per_day": 50,
                },
            },
            {
                "step": 6,
                "tool": "mcp__smartlead__smartlead_update_campaign_status",
                "args": {"campaign_id": "<campaign_id_from_step_1>", "status": "START"},
                "note": "EXECUTES the campaign — only call if --confirm",
            },
        ],
        "summary": {
            "campaign_name": campaign_name,
            "email_steps_count": len(email_steps),
            "leads_count": len(leads_smartlead),
            "ab_test": sequence_json.get("ab_test", False),
            "estimated_send_days": (len(leads_smartlead) // 50) + 1,
        },
    }

    return plan


def main():
    parser = argparse.ArgumentParser(
        description="SmartLead campaign upload from sequence JSON"
    )
    parser.add_argument(
        "--sequence-json", required=True, help="Path to sequence JSON portable"
    )
    parser.add_argument("--campaign-name", required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Default: dry-run (no API call)",
    )
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    parser.add_argument(
        "--confirm", action="store_true", help="Required for actual execution"
    )
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    seq_path = Path(args.sequence_json)
    if not seq_path.exists():
        print(f"❌ Sequence JSON not found: {seq_path}", file=sys.stderr)
        sys.exit(1)

    with open(seq_path) as f:
        sequence_json = json.load(f)

    # Validate structure
    required_keys = ["campaign_name", "steps", "leads", "channels"]
    missing = [k for k in required_keys if k not in sequence_json]
    if missing:
        print(f"❌ Sequence JSON missing keys: {missing}", file=sys.stderr)
        sys.exit(1)

    # Build plan
    plan = build_api_plan(sequence_json, args.campaign_name)

    # API key check
    if not args.dry_run:
        if not os.environ.get("SMARTLEAD_API_KEY"):
            print("❌ SMARTLEAD_API_KEY env var missing.", file=sys.stderr)
            print(
                "Add to ~/.zshrc: export SMARTLEAD_API_KEY='your_key'", file=sys.stderr
            )
            sys.exit(1)
        if not args.confirm:
            print("⚠️  --no-dry-run requires --confirm flag. Aborting.", file=sys.stderr)
            sys.exit(1)

    # Save plan
    Path(args.output_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    plan_path = Path(args.output_dir) / f"smartlead_upload_plan_{ts}.json"
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

    print(f"📋 SmartLead upload plan generated: {plan_path}")
    print(f"\nSummary:")
    print(f"  Campaign: {plan['summary']['campaign_name']}")
    print(f"  Email steps: {plan['summary']['email_steps_count']}")
    print(f"  Leads: {plan['summary']['leads_count']}")
    print(f"  A/B test: {plan['summary']['ab_test']}")
    print(
        f"  Estimated send window: {plan['summary']['estimated_send_days']} business days"
    )

    if args.dry_run:
        print(f"\n🔍 DRY-RUN mode — no API call made.")
        print(f"To execute: --no-dry-run --confirm")
    else:
        print(f"\n🚀 Ready to execute via subagent MCP calls.")
        print(
            f"   Subagent should iterate `plan.execution_order` and invoke each tool."
        )


if __name__ == "__main__":
    main()
