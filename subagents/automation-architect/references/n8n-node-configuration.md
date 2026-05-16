# n8n Node Configuration — Best Practice 2026

> Reference for `/automation-architect`. Source: `~/.claude/skills/n8n-node-configuration/` (913 lines OPERATION_PATTERNS + 789 DEPENDENCIES).

## HTTP Request — config baseline

```json
{
  "method": "POST",
  "url": "https://api.example.com/v1/...",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": { "parameters": [...] },
  "sendBody": true,
  "contentType": "json",
  "jsonParameters": "...",
  "options": {
    "timeout": 5000,
    "retryOnFail": true,
    "maxRetries": 3
  }
}
```

**Key settings**:
- `timeout: 5000` (5s, default 5min troppo lungo)
- `retryOnFail: true` + `maxRetries: 3`
- `redirect.followRedirects: true` (auto)
- `pagination.paginationMode`: per APIs paginate
- Response: `responseFormat: 'json'` (auto-parse)

## Code node — JS vs Python

| Use case | Choose | Why |
|----------|--------|-----|
| Data transform | **JS** | Faster startup, more samples |
| Date math (Luxon) | **JS** | Built-in `DateTime` available |
| Numeric / pandas-like | **Python** | Pandas, numpy via PyPI subset |
| Regex / string parsing | Either | JS preferred for ecosystem |
| HTTP from inside | JS: `$helpers.httpRequest()` / Python: `_helpers.http_request()` | Both supported |

**JS template**:
```javascript
// Process each input item
for (const item of $input.all()) {
  item.json.processed = item.json.value * 2;
  item.json.timestamp = $now.toISO();
}
return $input.all();
```

**Python template**:
```python
items = _input.all()
for item in items:
    item.json['processed'] = item.json['value'] * 2
return items
```

## Set vs Edit Fields vs Code

- **Set / Edit Fields**: 90% dei casi — rename, add literal, copy field, simple expression
- **Code**: solo se logica > 5 righe o needs loops/conditionals complex
- Anti-pattern: Code node per `{result: $json.value + 1}` → use Set

## Database nodes pattern

### Postgres / MySQL

```json
{
  "operation": "executeQuery",
  "query": "SELECT id, email FROM users WHERE created_at > $1 LIMIT 100",
  "additionalFields": {
    "queryParameters": "={{ $json.lastRunAt }}"
  }
}
```

**Key**:
- Parameterize queries (no string concat → SQL injection)
- LIMIT esplicito
- Connection pool size in n8n credential settings

## AI Agent node 2026

```json
{
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "agent": "openAiFunctionsAgent",
    "promptType": "define",
    "text": "You are a helpful assistant...",
    "options": {
      "maxIterations": 10,
      "returnIntermediateSteps": false,
      "systemMessage": "..."
    }
  }
}
```

**Sub-nodes**:
- Chat Model: `@n8n/n8n-nodes-langchain.lmChatAnthropic`
- Memory: `@n8n/n8n-nodes-langchain.memoryBufferWindow`
- Tools: HTTP Request Tool, MCP Client Tool, Code Tool, Workflow Tool

## See also

- `~/.claude/skills/n8n-node-configuration/SKILL.md` — full node-by-node guide
- `references/n8n-expression-syntax.md` — expression rules
