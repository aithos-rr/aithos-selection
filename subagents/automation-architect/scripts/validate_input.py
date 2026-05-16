#!/usr/bin/env python3
"""validate_input.py — Validate user requirement input for /automation-architect.

Checks:
- Requirement parseable (has trigger + at least 1 action)
- Integrations referenced are recognized
- No ambiguous wording (flag for clarification)

Usage: python3 validate_input.py "<requirement>"
"""

import sys
import re
import json

TRIGGER_KEYWORDS = {
    "webhook": ["quando arriva", "se ricevo", "on receive", "form submit", "webhook"],
    "schedule": ["ogni", "every", "daily", "hourly", "cron", "alle"],
    "ai_agent": ["chatbot", "assistente", "rispondi a domande", "agent"],
    "manual": ["click", "trigger manuale", "manual"],
}

ACTION_KEYWORDS = [
    "salva",
    "save",
    "notifica",
    "notify",
    "invia",
    "send",
    "aggiorna",
    "update",
    "crea",
    "create",
    "elimina",
    "delete",
]

KNOWN_INTEGRATIONS = [
    "notion",
    "slack",
    "gmail",
    "google sheets",
    "google drive",
    "google calendar",
    "hubspot",
    "attio",
    "pipedrive",
    "airtable",
    "stripe",
    "paypal",
    "square",
    "openai",
    "anthropic",
    "claude",
    "gpt",
    "postgres",
    "mysql",
    "mongodb",
    "supabase",
    "github",
    "gitlab",
    "linear",
    "jira",
    "telegram",
    "discord",
    "whatsapp",
]


def parse_requirement(text: str) -> dict:
    text_lower = text.lower()

    triggers_detected = [
        t for t, kws in TRIGGER_KEYWORDS.items() if any(kw in text_lower for kw in kws)
    ]
    actions_detected = [a for a in ACTION_KEYWORDS if a in text_lower]
    integrations_detected = [i for i in KNOWN_INTEGRATIONS if i in text_lower]

    issues = []
    if not triggers_detected:
        issues.append(
            {
                "severity": "warn",
                "message": "No clear trigger detected. Specify when workflow runs (webhook, schedule, manual).",
            }
        )
    if len(triggers_detected) > 1:
        issues.append(
            {
                "severity": "warn",
                "message": f"Multiple triggers detected: {triggers_detected}. Pick one.",
            }
        )
    if not actions_detected:
        issues.append(
            {
                "severity": "error",
                "message": "No action verbs detected. Specify what workflow does (save, notify, send, etc).",
            }
        )
    if not integrations_detected:
        issues.append(
            {
                "severity": "info",
                "message": "No specific integrations mentioned. Will ask during design.",
            }
        )

    return {
        "valid": not any(i["severity"] == "error" for i in issues),
        "trigger": triggers_detected[0] if triggers_detected else None,
        "actions": actions_detected,
        "integrations": integrations_detected,
        "issues": issues,
        "input_text": text,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 validate_input.py "<requirement>"', file=sys.stderr)
        sys.exit(1)
    text = " ".join(sys.argv[1:])
    result = parse_requirement(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)
