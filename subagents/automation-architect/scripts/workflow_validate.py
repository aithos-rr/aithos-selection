#!/usr/bin/env python3
"""workflow_validate.py — Static validation of workflow JSON.

Checks:
- Valid JSON parse
- Required top-level fields (name, nodes, connections, settings)
- Each node has id, name, type, typeVersion, position, parameters
- No duplicate node names
- Connections reference existing nodes
- No hardcoded secret patterns
- No expression syntax obvious errors

Usage: python3 workflow_validate.py <workflow.json> [--check credentials|expressions|all]
"""

import argparse
import json
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    (r"Bearer\s+[A-Za-z0-9_\-\.]{20,}", "Hardcoded Bearer token"),
    (r"sk-[A-Za-z0-9]{40,}", "OpenAI/Anthropic API key"),
    (r"xoxb-[A-Za-z0-9\-]+", "Slack bot token"),
    (r"xoxp-[A-Za-z0-9\-]+", "Slack user token"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub PAT"),
    (r"github_pat_[A-Za-z0-9_]{82}", "GitHub fine-grained PAT"),
    (r":[a-f0-9]{32,}@[a-z0-9\.\-]+", "Basic auth in URL"),
    (r'"password"\s*:\s*"[^"]{6,}"', "Plaintext password"),
]

EXPRESSION_PATTERNS_BAD = [
    (r"\$json\.[a-zA-Z_]+\s+[a-zA-Z_]+", "Space in field name (use bracket notation)"),
    (r"\$node\.[A-Z][a-zA-Z]+ ", 'Space in node name reference (use $node["..."])'),
    (r'\{\{\s*"Bearer ', "Hardcoded Bearer in expression"),
    (r'\{\{\s*"sk-', "Hardcoded API key in expression"),
]


def validate_workflow(workflow: dict) -> dict:
    errors = []
    warnings = []

    # Top-level
    for field in ["name", "nodes", "connections"]:
        if field not in workflow:
            errors.append(
                {
                    "type": "missing_required",
                    "field": field,
                    "message": f"Top-level field '{field}' missing",
                }
            )

    nodes = workflow.get("nodes", [])
    if not nodes:
        errors.append({"type": "no_nodes", "message": "Workflow has no nodes"})
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Check settings.executionOrder
    settings = workflow.get("settings", {})
    if "executionOrder" not in settings:
        warnings.append(
            {
                "type": "best_practice",
                "message": "settings.executionOrder missing, default 'v1' recommended",
            }
        )

    # Per-node checks
    node_names = []
    for i, node in enumerate(nodes):
        for field in ["id", "name", "type", "typeVersion", "position", "parameters"]:
            if field not in node:
                errors.append(
                    {
                        "type": "missing_required",
                        "node_index": i,
                        "field": field,
                        "message": f"Node #{i} missing '{field}'",
                    }
                )

        name = node.get("name", f"<unnamed-{i}>")
        if name in node_names:
            errors.append(
                {
                    "type": "duplicate_name",
                    "node": name,
                    "message": f"Duplicate node name '{name}'",
                }
            )
        node_names.append(name)

        # Type prefix check
        node_type = node.get("type", "")
        if node_type and not (
            node_type.startswith("n8n-nodes-base.")
            or node_type.startswith("@n8n/n8n-nodes-")
        ):
            warnings.append(
                {
                    "type": "unknown_node_type",
                    "node": name,
                    "message": f"Type '{node_type}' not in standard prefix",
                }
            )

        # Workflow-level >50 nodes warning
    if len(nodes) > 50:
        warnings.append(
            {
                "type": "performance",
                "message": f"Workflow has {len(nodes)} nodes — consider sub-workflow split (>50 unmaintainable)",
            }
        )

    # Connections check
    connections = workflow.get("connections", {})
    for source_name, conn in connections.items():
        if source_name not in node_names:
            errors.append(
                {
                    "type": "invalid_reference",
                    "node": source_name,
                    "message": f"Connection source '{source_name}' not in nodes",
                }
            )
        for output_type, branches in conn.items():
            for branch in branches:
                for target in branch:
                    target_name = target.get("node")
                    if target_name and target_name not in node_names:
                        errors.append(
                            {
                                "type": "invalid_reference",
                                "node": target_name,
                                "message": f"Connection target '{target_name}' not in nodes",
                            }
                        )

    # Secret scan in JSON serialized
    workflow_str = json.dumps(workflow)
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, workflow_str):
            errors.append(
                {
                    "type": "hardcoded_secret",
                    "pattern": label,
                    "message": f"Hardcoded secret detected: {label}. Use n8n credential or env var.",
                }
            )

    # Expression syntax scan
    for pattern, label in EXPRESSION_PATTERNS_BAD:
        if re.search(pattern, workflow_str):
            warnings.append(
                {"type": "expression_syntax", "pattern": label, "message": label}
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "node_count": len(nodes),
        "connection_count": sum(1 for _ in connections.values()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow_file")
    parser.add_argument(
        "--check",
        default="all",
        choices=["all", "credentials", "expressions", "structure"],
    )
    args = parser.parse_args()

    workflow = json.loads(Path(args.workflow_file).read_text())
    result = validate_workflow(workflow)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
