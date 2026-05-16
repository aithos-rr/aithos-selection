#!/usr/bin/env python3
"""
personalize_first_line.py — CLI wrapper for personalization-engine skill

Usage:
    python personalize_first_line.py --leads-json <path> --voice direct \\
        --value-prop "..." --output-dir output [--variant-count 3]

Note: questo script genera i prompt template per LLM call, salva il file di
input + struttura output. La generazione first-line vera richiede call LLM
(Claude via subagent flow). Qui produciamo il payload.

Output: prompt-payload + struttura per ogni lead, ready for LLM call.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SIGNAL_TO_HOOK = {
    "job_change": 1,
    "funding_round": 2,
    "hiring_surge": 3,
    "podcast_guest": 4,
    "recent_post": 5,
    "conference": 6,
    "tool_stack_change": 7,
    "geo_event": 8,
}

BANNED_MARKERS = [
    "delve into",
    "navigate the landscape",
    "I hope this email finds you well",
    "leverage",
    "synergy",
    "seamlessly",
    "cutting-edge",
    "unlock the potential",
    "robust solution",
    "in today's fast-paced world",
]

VOICE_DESCRIPTORS = {
    "direct": "factual, no filler, 12-18 word, no emoji",
    "friendly": "conversational, 1-2 emoji ok, 15-22 word",
    "educational": "data-first, dato concreto in apertura, 18-25 word",
    "bold": "contrarian view, hook forte, 15-25 word",
}


def select_top_signal(intent_signals, max_age_days=90):
    """Select most recent + highest priority signal."""
    if not intent_signals:
        return None

    today = datetime.now()
    valid = []
    for sig in intent_signals:
        try:
            sig_date = datetime.fromisoformat(
                sig.get("date", "").replace("Z", "+00:00").split("+")[0]
            )
            age_days = (today - sig_date).days
            if age_days <= max_age_days:
                priority = (
                    list(SIGNAL_TO_HOOK.keys()).index(sig.get("type", ""))
                    if sig.get("type") in SIGNAL_TO_HOOK
                    else 99
                )
                valid.append({"sig": sig, "age": age_days, "priority": priority})
        except (ValueError, TypeError):
            continue

    if not valid:
        return None

    # Sort by priority (lower = better) then age (lower = better)
    valid.sort(key=lambda x: (x["priority"], x["age"]))
    return valid[0]["sig"]


def build_prompt_payload(lead, brand_voice, value_prop, variant_count=3):
    """Build LLM prompt payload for first-line generation."""
    top_signal = select_top_signal(lead.get("intent_signals", []))

    if not top_signal:
        return {
            "lead_id": lead.get("lead_id", lead.get("email", "unknown")),
            "skipped": True,
            "skip_reason": "no_recent_signal_in_90d",
        }

    hook_template_id = SIGNAL_TO_HOOK.get(top_signal["type"], 0)

    system_prompt = f"""Sei un copywriter esperto di cold email B2B. Genera SOLO la prima riga di un email cold outreach in italiano.

VINCOLI MANDATORY:
- Max 25 parole
- Riferisci il signal specifico fornito (NO generic)
- Tone: {brand_voice} ({VOICE_DESCRIPTORS.get(brand_voice, "")})
- NO marker stilistici banned: {", ".join(BANNED_MARKERS[:5])}, ecc.
- NO em-dash multipli (max 1 per frase)
- Conversational, come scriveresti a collega

OUTPUT: SOLO il testo first-line, nessuna spiegazione."""

    user_prompts = []
    for v in ["A", "B", "C"][:variant_count]:
        prompt = f"""Lead: {lead.get("first_name", "")} {lead.get("last_name", "")}, {lead.get("role", "professional")} a {lead.get("company", "")}, industry {lead.get("industry", "B2B")}.
Signal: {top_signal["type"]} = "{top_signal["value"]}" ({top_signal.get("date", "recent")})
Brand voice: {brand_voice}
Value prop context: {value_prop}
Genera variant {v} basata su template hook #{hook_template_id} (vedi references/prompt-patterns.md)."""
        user_prompts.append({"variant": v, "prompt": prompt})

    return {
        "lead_id": lead.get("lead_id", lead.get("email", "unknown")),
        "lead_email": lead.get("email"),
        "signal_used": top_signal["type"],
        "signal_value": top_signal["value"],
        "hook_template_id": hook_template_id,
        "system_prompt": system_prompt,
        "user_prompts": user_prompts,
        "_meta": {
            "generated_at": datetime.now().isoformat(),
            "brand_voice": brand_voice,
            "variant_count": variant_count,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Build personalization prompt payload")
    parser.add_argument(
        "--leads-json", required=True, help="Path to leads validated JSON"
    )
    parser.add_argument(
        "--voice",
        choices=["direct", "friendly", "educational", "bold"],
        default="direct",
    )
    parser.add_argument(
        "--value-prop", required=True, help="Brand value proposition (1-2 sentences)"
    )
    parser.add_argument("--variant-count", type=int, default=3)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    leads_path = Path(args.leads_json)
    if not leads_path.exists():
        print(f"❌ File not found: {leads_path}", file=sys.stderr)
        sys.exit(1)

    with open(leads_path) as f:
        data = json.load(f)

    leads = data.get("compliant_leads", data) if isinstance(data, dict) else data

    # Parse intent_signals if string (from CSV)
    for lead in leads:
        if isinstance(lead.get("intent_signals"), str):
            try:
                lead["intent_signals"] = json.loads(lead["intent_signals"])
            except json.JSONDecodeError:
                lead["intent_signals"] = []

    payloads = []
    skipped = 0
    for lead in leads:
        payload = build_prompt_payload(
            lead, args.voice, args.value_prop, args.variant_count
        )
        if payload.get("skipped"):
            skipped += 1
        payloads.append(payload)

    # Save
    Path(args.output_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = Path(args.output_dir) / f"personalization_payloads_{ts}.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "created_at": datetime.now().isoformat(),
                "voice": args.voice,
                "value_prop": args.value_prop,
                "variant_count": args.variant_count,
                "summary": {
                    "total_leads": len(leads),
                    "personalizable": len(leads) - skipped,
                    "skipped_no_signal": skipped,
                },
                "payloads": payloads,
            },
            f,
            indent=2,
            default=str,
        )

    print(
        f"✓ Built {len(leads) - skipped} personalization payloads ({skipped} skipped, no signal)."
    )
    print(f"  Saved: {output_path}")
    print(
        f"\nNext: subagent invoke LLM call per ogni payload (Claude Sonnet) → first-line variants."
    )


if __name__ == "__main__":
    main()
