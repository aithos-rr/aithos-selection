# n8n Expression Syntax — Critical Rules

> Reference for `/automation-architect`. Source: `~/.claude/skills/n8n-expression-syntax/` (516 SKILL + 393 COMMON_MISTAKES + 483 EXAMPLES).

## Core syntax

| Expression | Meaning |
|------------|---------|
| `{{ ... }}` | Wrap any expression for evaluation |
| `$json` | Current item JSON |
| `$json.field` | Access field |
| `$json['field with space']` | Bracket notation for spaces |
| `$node["Node Name"].json` | Access another node's output |
| `$input.first().json` | First item from input |
| `$input.all()` | All items array |
| `$input.last().json` | Last item |
| `$now` | Luxon DateTime now |
| `$today` | Today midnight |
| `$workflow.id` | Current workflow ID |
| `$execution.id` | Current execution ID |
| `$env.MY_VAR` | Environment variable |

## Top 10 Pitfalls (must avoid)

### 1. Missing `{{ }}` braces

```
❌ $json.email
✅ {{$json.email}}
```

### 2. Webhook body access

Webhook node wraps user data under `.body`:

```
❌ {{$json.email}}
✅ {{$json.body.email}}
```

Webhook structure:
```json
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": { "email": "..." }
}
```

### 3. Spaces in field names

```
❌ {{$json.first name}}
✅ {{$json['first name']}}
```

### 4. Spaces in node names

```
❌ {{$node.HTTP Request.json.data}}
✅ {{$node["HTTP Request"].json.data}}
```

### 5. Multi-item indexing

```
❌ {{$json.field}}        // only first item shown in UI
✅ {{$input.all()[0].json.field}}  // first item explicit
✅ {{$input.first().json.field}}   // alternative
```

### 6. Date formatting

```
❌ {{new Date().toISOString()}}    // works but verbose
✅ {{$now.toISO()}}
✅ {{$now.toFormat('yyyy-MM-dd')}}
✅ {{$now.minus({ days: 7 }).toISO()}}
```

### 7. Conditional in expression

```
❌ {{$json.value && 'yes' || 'no'}}     // hard to read
✅ Use IF node instead
✅ {{$json.value ? 'yes' : 'no'}}        // ternary OK for simple
```

### 8. Credential leak in expression

```
❌ {{ "Bearer abc123" }}                 // hardcoded secret
✅ Use n8n Credential (managed)
✅ {{$env.API_KEY}}                      // env var
```

### 9. `$input.first()` vs `$input.all()`

- `$input.first()` → first item, single
- `$input.all()` → all items, array
- `$input.last()` → last item

### 10. Python vs JS syntax

Code node Python uses `_input` (underscore), JS uses `$input` (dollar):

```javascript
// JS
return $input.all().map(item => ...);
```

```python
# Python
return [item for item in _input.all()]
```

## Common helpful expressions

```javascript
// Format currency
{{$json.amount.toLocaleString('it-IT', {style:'currency', currency:'EUR'})}}

// Hash for idempotency
{{ $crypto.createHash('sha256').update($json.body.email).digest('hex') }}

// Default value
{{ $json.optional || 'default' }}

// Array join
{{ $json.tags.join(', ') }}

// Object to query string
{{ Object.entries($json.params).map(([k,v]) => `${k}=${v}`).join('&') }}

// Slack mention
{{ '<@' + $json.user_id + '>' }}

// Markdown bold
{{ '**' + $json.title + '**' }}
```

## See also

- `~/.claude/skills/n8n-expression-syntax/COMMON_MISTAKES.md` — full catalog
- `~/.claude/skills/n8n-expression-syntax/EXAMPLES.md` — 483 lines examples
