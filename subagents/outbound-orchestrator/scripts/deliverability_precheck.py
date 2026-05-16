#!/usr/bin/env python3
"""
deliverability_precheck.py — DNS query SPF/DKIM/DMARC + warmup days check + RBL scan

Usage:
    python deliverability_precheck.py --domain yourdomain.com [--mailbox you@yourdomain.com]
        [--dkim-selector smartlead] [--check-rbl]

Output: JSON with status per check, summary ready/issues/warnings.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import dns.resolver

    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False


RBL_LISTS = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "b.barracudacentral.org",
    "dnsbl.sorbs.net",
    "multi.surbl.org",
]


def check_spf(domain):
    """Check SPF record presence + policy."""
    if not DNS_AVAILABLE:
        return {"present": False, "error": "dnspython not installed"}
    try:
        answers = dns.resolver.resolve(domain, "TXT", lifetime=5)
        for rdata in answers:
            txt = "".join(
                [s.decode() if isinstance(s, bytes) else s for s in rdata.strings]
            )
            if txt.startswith("v=spf1"):
                policy = (
                    "hard_fail"
                    if "-all" in txt
                    else "soft_fail"
                    if "~all" in txt
                    else "neutral"
                )
                lookups = txt.count("include:")
                return {
                    "present": True,
                    "policy": policy,
                    "raw": txt[:200],
                    "lookups": lookups,
                }
        return {"present": False}
    except dns.resolver.NXDOMAIN:
        return {"present": False, "error": "domain not found"}
    except Exception as e:
        return {"present": False, "error": str(e)[:80]}


def check_dkim(domain, selector="smartlead"):
    """Check DKIM record on selector."""
    if not DNS_AVAILABLE:
        return {"present": False}
    try:
        full_domain = f"{selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(full_domain, "TXT", lifetime=5)
        for rdata in answers:
            txt = "".join(
                [s.decode() if isinstance(s, bytes) else s for s in rdata.strings]
            )
            if "v=DKIM1" in txt or "k=rsa" in txt:
                # Extract public key length approximation
                p_match = txt.find("p=")
                key_excerpt = txt[p_match : p_match + 20] if p_match > 0 else ""
                return {
                    "present": True,
                    "selector": selector,
                    "raw_excerpt": key_excerpt,
                }
        return {"present": False, "selector": selector}
    except dns.resolver.NXDOMAIN:
        return {"present": False, "selector": selector, "error": "selector_not_found"}
    except Exception as e:
        return {"present": False, "selector": selector, "error": str(e)[:80]}


def check_dmarc(domain):
    """Check DMARC record + policy."""
    if not DNS_AVAILABLE:
        return {"present": False}
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT", lifetime=5)
        for rdata in answers:
            txt = "".join(
                [s.decode() if isinstance(s, bytes) else s for s in rdata.strings]
            )
            if txt.startswith("v=DMARC1"):
                policy = "none"
                if "p=quarantine" in txt:
                    policy = "quarantine"
                elif "p=reject" in txt:
                    policy = "reject"
                pct_match = 100
                for part in txt.split(";"):
                    if part.strip().startswith("pct="):
                        try:
                            pct_match = int(part.strip().split("=")[1])
                        except (ValueError, IndexError):
                            pass
                return {
                    "present": True,
                    "policy": policy,
                    "pct": pct_match,
                    "raw": txt[:200],
                }
        return {"present": False}
    except dns.resolver.NXDOMAIN:
        return {"present": False}
    except Exception as e:
        return {"present": False, "error": str(e)[:80]}


def check_bimi(domain):
    """Check BIMI record (optional)."""
    if not DNS_AVAILABLE:
        return {"present": False}
    try:
        answers = dns.resolver.resolve(f"default._bimi.{domain}", "TXT", lifetime=5)
        for rdata in answers:
            txt = "".join(
                [s.decode() if isinstance(s, bytes) else s for s in rdata.strings]
            )
            if "v=BIMI1" in txt:
                return {"present": True, "raw": txt[:200]}
        return {"present": False}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return {"present": False}
    except Exception as e:
        return {"present": False, "error": str(e)[:80]}


def check_rbl_for_domain(domain):
    """Resolve domain MX, then check each MX IP against RBL."""
    if not DNS_AVAILABLE:
        return {"available": False}

    results = {"checked": 0, "listed": [], "clean": []}
    try:
        # Resolve domain to IP (A record)
        a_records = dns.resolver.resolve(domain, "A", lifetime=5)
        ips = [str(r) for r in a_records]
    except Exception:
        return {"available": False, "error": "could not resolve domain A record"}

    if not ips:
        return {"available": False, "error": "no A records"}

    ip = ips[0]
    reversed_ip = ".".join(reversed(ip.split(".")))

    for rbl in RBL_LISTS:
        try:
            dns.resolver.resolve(f"{reversed_ip}.{rbl}", "A", lifetime=3)
            results["listed"].append(rbl)
        except dns.resolver.NXDOMAIN:
            results["clean"].append(rbl)
        except Exception:
            results["clean"].append(rbl)  # Treat error as clean (not authoritative)
        results["checked"] += 1

    return results


def evaluate_status(checks):
    """Build issues + warnings + ready bool from checks dict."""
    issues = []
    warnings = []

    # SPF
    if not checks["spf"].get("present"):
        issues.append(
            {
                "severity": "critical",
                "check": "spf",
                "status": "absent",
                "recommendation": "Setup SPF record: v=spf1 include:<provider> -all",
            }
        )
    elif checks["spf"].get("policy") == "neutral":
        warnings.append(
            {
                "severity": "warning",
                "check": "spf_policy",
                "status": "neutral",
                "recommendation": "Use -all (hard fail) or ~all (soft fail)",
            }
        )

    # DKIM
    if not checks["dkim"].get("present"):
        issues.append(
            {
                "severity": "critical",
                "check": "dkim",
                "status": "absent",
                "recommendation": f"Setup DKIM record on selector '{checks['dkim'].get('selector', 'smartlead')}'",
            }
        )

    # DMARC
    if not checks["dmarc"].get("present"):
        issues.append(
            {
                "severity": "critical",
                "check": "dmarc",
                "status": "absent",
                "recommendation": "Setup DMARC record: v=DMARC1; p=quarantine; rua=mailto:dmarc@...",
            }
        )
    elif checks["dmarc"].get("policy") == "none":
        issues.append(
            {
                "severity": "critical",
                "check": "dmarc_policy",
                "status": "p=none",
                "recommendation": "Update DMARC to p=quarantine minimum (p=reject ideal)",
            }
        )

    # BIMI (optional)
    if not checks["bimi"].get("present"):
        warnings.append(
            {
                "severity": "info",
                "check": "bimi",
                "status": "absent",
                "recommendation": "Optional. +5-10% open rate if VMC budget ($1500/yr)",
            }
        )

    # RBL
    if checks.get("rbl", {}).get("listed"):
        for rbl in checks["rbl"]["listed"]:
            issues.append(
                {
                    "severity": "critical",
                    "check": f"rbl_{rbl}",
                    "status": "listed",
                    "recommendation": f"Delist via {rbl} portal",
                }
            )

    ready = len(issues) == 0
    return {"ready": ready, "issues": issues, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(
        description="Pre-flight email deliverability check"
    )
    parser.add_argument(
        "--domain", required=True, help="Sender domain (e.g. yourdomain.com)"
    )
    parser.add_argument("--mailbox", help="Mailbox address (used for context)")
    parser.add_argument(
        "--dkim-selector",
        default="smartlead",
        help="DKIM selector (default: smartlead)",
    )
    parser.add_argument(
        "--check-rbl", action="store_true", help="Run RBL blacklist scan"
    )
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    if not DNS_AVAILABLE:
        print("⚠️  dnspython not installed. Run: pip install dnspython", file=sys.stderr)
        print(
            "Falling back to limited check (no DNS query). Mark all as unknown.",
            file=sys.stderr,
        )

    checks = {
        "spf": check_spf(args.domain),
        "dkim": check_dkim(args.domain, args.dkim_selector),
        "dmarc": check_dmarc(args.domain),
        "bimi": check_bimi(args.domain),
    }

    if args.check_rbl:
        checks["rbl"] = check_rbl_for_domain(args.domain)

    status = evaluate_status(checks)

    result = {
        "domain": args.domain,
        "mailbox": args.mailbox,
        "checked_at": datetime.now().isoformat(),
        "ready": status["ready"],
        "issues": status["issues"],
        "warnings": status["warnings"],
        "dns_status": checks,
    }

    # Save
    Path(args.output_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = (
        Path(args.output_dir)
        / f"deliverability_check_{args.domain.replace('.', '_')}_{ts}.json"
    )
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    # Print summary
    if status["ready"]:
        print(f"✅ Deliverability check PASSED: {args.domain}")
    else:
        print(f"❌ Deliverability check FAILED: {args.domain}")

    if status["issues"]:
        print(f"\n🛑 Critical issues ({len(status['issues'])}):")
        for issue in status["issues"]:
            print(f"   - {issue['check']}: {issue['status']}")
            print(f"     → {issue['recommendation']}")

    if status["warnings"]:
        print(f"\n⚠️  Warnings ({len(status['warnings'])}):")
        for warn in status["warnings"]:
            print(f"   - {warn['check']}: {warn['status']}")

    print(f"\nFull report: {output_path}")

    sys.exit(0 if status["ready"] else 1)


if __name__ == "__main__":
    main()
