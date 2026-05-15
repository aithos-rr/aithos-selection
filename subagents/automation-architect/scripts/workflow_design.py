#!/usr/bin/env python3
"""workflow_design.py — Generate workflow JSON skeleton from pattern + requirement.

Reads pattern (webhook_driven|scheduled|ai_agent|data_pipeline) + requirement json,
emits skeleton workflow JSON ready for population.

Usage: python3 workflow_design.py --pattern webhook_driven --requirement requirement.json
"""

import argparse
import json
import sys
from pathlib import Path


def webhook_skeleton(name: str, path: str = "workflow") -> dict:
    return {
        "name": name,
        "nodes": [
            {
                "id": "1",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": path,
                    "responseMode": "responseNode",
                    "options": {},
                },
            },
            {
                "id": "2",
                "name": "Set",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [460, 300],
                "parameters": {"fields": {"values": []}, "options": {}},
            },
            {
                "id": "999",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [880, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": '={{ {"received": true} }}',
                },
            },
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Set", "type": "main", "index": 0}]]},
            "Set": {
                "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
            },
        },
        "settings": {
            "executionOrder": "v1",
            "saveExecutionProgress": True,
            "saveManualExecutions": True,
        },
        "staticData": {},
    }


def scheduled_skeleton(name: str, interval_hours: int = 1) -> dict:
    return {
        "name": name,
        "nodes": [
            {
                "id": "1",
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.1,
                "position": [240, 300],
                "parameters": {
                    "rule": {
                        "interval": [
                            {"field": "hours", "hoursInterval": interval_hours}
                        ]
                    }
                },
            }
        ],
        "connections": {},
        "settings": {"executionOrder": "v1"},
        "staticData": {},
    }


def ai_agent_skeleton(name: str, model: str = "claude-sonnet-4-6") -> dict:
    return {
        "name": name,
        "nodes": [
            {
                "id": "1",
                "name": "When chat message received",
                "type": "@n8n/n8n-nodes-langchain.chatTrigger",
                "typeVersion": 1.1,
                "position": [240, 300],
                "parameters": {"options": {}},
            },
            {
                "id": "2",
                "name": "AI Agent",
                "type": "@n8n/n8n-nodes-langchain.agent",
                "typeVersion": 1.5,
                "position": [460, 300],
                "parameters": {
                    "agent": "openAiFunctionsAgent",
                    "options": {"maxIterations": 10},
                },
            },
            {
                "id": "3",
                "name": "Anthropic Chat Model",
                "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
                "typeVersion": 1,
                "position": [380, 480],
                "parameters": {"model": model, "options": {}},
            },
            {
                "id": "4",
                "name": "Window Memory",
                "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
                "typeVersion": 1,
                "position": [540, 480],
                "parameters": {"contextWindowLength": 10},
            },
        ],
        "connections": {
            "When chat message received": {
                "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
            },
            "Anthropic Chat Model": {
                "ai_languageModel": [
                    [{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]
                ]
            },
            "Window Memory": {
                "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
            },
        },
        "settings": {"executionOrder": "v1"},
        "staticData": {},
    }


def data_pipeline_skeleton(name: str) -> dict:
    return {
        "name": name,
        "nodes": [
            {
                "id": "1",
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.1,
                "position": [240, 300],
                "parameters": {
                    "rule": {"interval": [{"field": "hours", "hoursInterval": 6}]}
                },
            },
            {
                "id": "2",
                "name": "HTTP Request (source)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [460, 300],
                "parameters": {
                    "method": "GET",
                    "url": "https://api.example.com/data",
                    "options": {"timeout": 5000, "retryOnFail": True, "maxTries": 3},
                },
            },
            {
                "id": "3",
                "name": "Code (transform)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300],
                "parameters": {"jsCode": "// transform here\nreturn $input.all();"},
            },
        ],
        "connections": {
            "Schedule Trigger": {
                "main": [
                    [{"node": "HTTP Request (source)", "type": "main", "index": 0}]
                ]
            },
            "HTTP Request (source)": {
                "main": [[{"node": "Code (transform)", "type": "main", "index": 0}]]
            },
        },
        "settings": {"executionOrder": "v1"},
        "staticData": {},
    }


PATTERN_GENERATORS = {
    "webhook_driven": webhook_skeleton,
    "scheduled": scheduled_skeleton,
    "ai_agent": ai_agent_skeleton,
    "data_pipeline": data_pipeline_skeleton,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pattern", required=True, choices=list(PATTERN_GENERATORS.keys())
    )
    parser.add_argument("--name", default="generated-workflow")
    parser.add_argument("--output", default="-", help="Output file or - for stdout")
    parser.add_argument(
        "--path", default="workflow", help="Webhook path (only for webhook_driven)"
    )
    args = parser.parse_args()

    gen = PATTERN_GENERATORS[args.pattern]
    if args.pattern == "webhook_driven":
        skeleton = gen(args.name, args.path)
    else:
        skeleton = gen(args.name)

    output_str = json.dumps(skeleton, indent=2, ensure_ascii=False)

    if args.output == "-":
        print(output_str)
    else:
        Path(args.output).write_text(output_str)
        print(f"✓ Skeleton written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
