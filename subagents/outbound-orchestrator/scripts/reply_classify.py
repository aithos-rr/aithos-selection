#!/usr/bin/env python3
"""
reply_classify.py — Hybrid rule-based + LLM-fallback reply classification

Usage:
    python reply_classify.py --reply-json <path> [--threshold 0.85]

Input JSON: {from_email, subject, body, headers (optional), lead_context}
Output: classification {class, confidence, action, smartlead_category, ...}

5 classes: positive, negative, OOO, unsubscribe, bounce.
Rule-based catches 70-80% (DSN, OOO, explicit unsubscribe, clear positive/negative).
Ambigui (rule confidence < threshold) → flag for LLM fallback (subagent invokes LLM).
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# DSN bounce patterns
DSN_HEADERS = ["X-Failed-Recipients", "Diagnostic-Code"]
DSN_PATTERNS = [
    r"550\s+5\.",
    r"5\.[0-9]\.[0-9]",
    r"recipient\s+address\s+rejected",
    r"mailbox.*not\s*found",
    r"address.*does\s*not\s*exist",
    r"user\s+unknown",
    r"mailbox.*full",
    r"delivery.*failed",
]

# OOO patterns
OOO_KEYWORDS = [
    # Italian
    "fuori ufficio",
    "in vacanza",
    "in ferie",
    "rientro il",
    "tornerò il",
    "non sono in ufficio",
    "assente fino al",
    "out of office",
    # English
    "out of office",
    "ooo",
    "vacation",
    "annual leave",
    "returning on",
    "be back on",
    "currently away",
    "i am out",
    "i'm out",
    "automatic reply",
    "auto-reply",
]

# Unsubscribe patterns
UNSUBSCRIBE_KEYWORDS = [
    # Italian
    "disiscrivimi",
    "disiscriviti",
    "rimuovere",
    "non scrivere",
    "non più",
    "smetti",
    "elimina dalla lista",
    # English
    "unsubscribe",
    "remove me",
    "stop sending",
    "do not contact",
    "take me off",
    "don't email me",
    "stop emailing",
]

# Negative explicit
NEGATIVE_KEYWORDS = [
    # Italian
    "non mi interessa",
    "non interessato",
    "non interessata",
    "abbiamo già",
    "non è il momento",
    "no grazie",
    "non sono la persona",
    "non posso aiutarti",
    # English
    "not interested",
    "we have",
    "no thanks",
    "wrong person",
    "not now",
    "pass",
    "not a fit",
    "not for us",
]

# Positive
POSITIVE_KEYWORDS = [
    # Italian
    "interessato",
    "interessante",
    "schedulare",
    "incontriamoci",
    "prenotare",
    "vediamoci",
    "dimmi di più",
    "ne parliamo",
    "demo",
    "call",
    "calendly",
    # English
    "interested",
    "schedule",
    "demo",
    "meeting",
    "call",
    "calendly",
    "let's chat",
    "tell me more",
    "yes please",
    "sounds good",
    "let's set up",
    "happy to",
]

# OOO date extraction patterns
OOO_DATE_PATTERNS = [
    r"return(?:ing|s)?\s+(?:on\s+)?(\d{1,2}[\/\-\s][A-Za-z]+(?:\s+\d{2,4})?)",
    r"back\s+(?:on\s+)?(\d{1,2}[\/\-\s][A-Za-z]+)",
    r"rientro(?:\s+il)?\s+(\d{1,2}[\/\-\s][A-Za-z]+)",
    r"tornerò\s+(?:il\s+)?(\d{1,2}[\/\-\s][A-Za-z]+)",
    r"fino\s+al\s+(\d{1,2}[\/\-\s][A-Za-z]+)",
    r"until\s+(\d{1,2}[\/\-\s][A-Za-z]+)",
]


def is_bounce(reply):
    """DSN-based bounce detection."""
    body_lower = (reply.get("body", "") or "").lower()
    headers = reply.get("headers", {}) or {}

    for h in DSN_HEADERS:
        if h in headers:
            return True, "dsn_header_present", 1.0

    for pattern in DSN_PATTERNS:
        if re.search(pattern, body_lower):
            return True, f"smtp_pattern_{pattern[:20]}", 0.95

    return False, None, 0.0


def is_ooo(body_lower):
    """OOO keyword detection."""
    matches = [kw for kw in OOO_KEYWORDS if kw in body_lower]
    if matches:
        return True, matches, 0.93
    return False, [], 0.0


def is_unsubscribe(body_lower):
    """Unsubscribe explicit."""
    matches = [kw for kw in UNSUBSCRIBE_KEYWORDS if kw in body_lower]
    if matches:
        return True, matches, 0.95
    return False, [], 0.0


def is_negative(body_lower):
    """Negative reply detection (multi-keyword required)."""
    matches = [kw for kw in NEGATIVE_KEYWORDS if kw in body_lower]
    if len(matches) >= 1:
        confidence = min(0.85 + 0.05 * len(matches), 0.95)
        return True, matches, confidence
    return False, [], 0.0


def is_positive(body_lower):
    """Positive reply detection (need 2+ matches for confidence)."""
    matches = [kw for kw in POSITIVE_KEYWORDS if kw in body_lower]
    if len(matches) >= 2:
        confidence = min(0.85 + 0.04 * len(matches), 0.96)
        return True, matches, confidence
    elif len(matches) == 1:
        return True, matches, 0.70  # ambiguous, may need LLM
    return False, [], 0.0


def extract_return_date(body):
    """Try to extract OOO return date."""
    for pattern in OOO_DATE_PATTERNS:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def classify_reply(reply, threshold=0.85):
    """Hybrid rule-based classification.

    Returns classification dict with `manual_triage: True` if confidence < threshold,
    indicating subagent should invoke LLM fallback.
    """
    body = reply.get("body", "") or ""
    body_lower = body.lower()

    # 1. Bounce (highest priority — DSN)
    bounced, reason, conf = is_bounce(reply)
    if bounced:
        return {
            "class": "bounce",
            "confidence": conf,
            "method": "rule_based_dsn",
            "action": "suppress_hard",
            "smartlead_category": "Hard-Bounce",
            "details": {"bounce_reason": reason},
            "manual_triage": False,
        }

    # 2. Unsubscribe (explicit)
    unsub, matches, conf = is_unsubscribe(body_lower)
    if unsub:
        return {
            "class": "unsubscribe",
            "confidence": conf,
            "method": "rule_based",
            "action": "suppress_cross_stack",
            "smartlead_category": "Do-Not-Contact",
            "details": {"matched_keywords": matches},
            "manual_triage": False,
        }

    # 3. OOO
    ooo, matches, conf = is_ooo(body_lower)
    if ooo:
        return_date = extract_return_date(body)
        snooze_until = return_date or (datetime.now() + timedelta(days=10)).isoformat()
        return {
            "class": "OOO",
            "confidence": conf,
            "method": "rule_based",
            "action": "snooze",
            "snooze_until": snooze_until,
            "smartlead_category": "Out-of-Office",
            "details": {
                "matched_keywords": matches,
                "return_date_extracted": return_date,
            },
            "manual_triage": False,
        }

    # 4. Positive (check before negative — explicit positive often clear)
    pos, pos_matches, pos_conf = is_positive(body_lower)
    neg, neg_matches, neg_conf = is_negative(body_lower)

    # Conflict resolution: if both positive AND negative match, manual triage
    if pos and neg:
        return {
            "class": "ambiguous",
            "confidence": 0.5,
            "method": "rule_based_conflict",
            "action": "manual_triage_required",
            "details": {
                "positive_keywords": pos_matches,
                "negative_keywords": neg_matches,
                "reasoning": "Both positive and negative signals — likely 'wrong person' or polite decline",
            },
            "manual_triage": True,
        }

    if pos and pos_conf >= threshold:
        return {
            "class": "positive",
            "confidence": pos_conf,
            "method": "rule_based",
            "action": "pause_sequence_and_forward",
            "smartlead_category": "Interested",
            "details": {
                "matched_keywords": pos_matches,
                "intent_detected": "meeting_request_likely",
            },
            "manual_triage": False,
        }

    if neg and neg_conf >= threshold:
        return {
            "class": "negative",
            "confidence": neg_conf,
            "method": "rule_based",
            "action": "pause_lead",
            "smartlead_category": "Not-Interested",
            "details": {"matched_keywords": neg_matches},
            "manual_triage": False,
        }

    # 5. Ambiguous → flag for LLM fallback
    return {
        "class": "ambiguous",
        "confidence": max(pos_conf, neg_conf, 0.5),
        "method": "rule_based_low_confidence",
        "action": "manual_triage_required",
        "details": {
            "positive_match_count": len(pos_matches),
            "negative_match_count": len(neg_matches),
            "reasoning": "Low confidence rule-based. Subagent should invoke LLM fallback.",
        },
        "manual_triage": True,
        "llm_fallback_needed": True,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Classify cold email reply (5-class hybrid)"
    )
    parser.add_argument("--reply-json", required=True, help="Path to reply JSON")
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    reply_path = Path(args.reply_json)
    if not reply_path.exists():
        print(f"❌ Reply JSON not found: {reply_path}", file=sys.stderr)
        sys.exit(1)

    with open(reply_path) as f:
        data = json.load(f)

    reply = data.get("reply", data)
    classification = classify_reply(reply, args.threshold)

    # Save
    Path(args.output_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(args.output_dir) / f"reply_classification_{ts}.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "classified_at": datetime.now().isoformat(),
                "reply_excerpt": reply.get("body", "")[:200],
                "from_email": reply.get("from_email"),
                "classification": classification,
            },
            f,
            indent=2,
        )

    # Print summary
    print(f"📧 Reply classification:")
    print(f"  Class: {classification['class']}")
    print(f"  Confidence: {classification['confidence']:.2f}")
    print(f"  Method: {classification['method']}")
    print(f"  Action: {classification['action']}")
    if classification.get("manual_triage"):
        print(f"  ⚠️  Manual triage flagged. LLM fallback recommended.")
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
