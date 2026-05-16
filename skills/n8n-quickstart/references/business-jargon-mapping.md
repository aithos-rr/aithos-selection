# Traduzione jargon n8n → linguaggio business

Per il pubblico Learnn non-dev, usa queste traduzioni quando spieghi nodi e concetti n8n.

| Termine n8n | Spiegazione business |
|-------------|---------------------|
| **Workflow** | Sequenza automatica di passi (come una "pipeline" di lavoro) |
| **Node** | Un singolo passo del workflow (es. "manda email", "leggi dal database") |
| **Trigger** | L'evento che fa partire il workflow (un orario, una chiamata da fuori, un click) |
| **Webhook** | Un "indirizzo" dove altri servizi possono mandare notifiche al tuo workflow |
| **Code node** | Un passo custom che esegue codice tu scrivi (JavaScript o Python) — usa solo se i nodi esistenti non bastano |
| **Expression** | Una formula inline stile Excel per trasformare dati al volo — `{{ $json.email }}` = "prendi il campo email dall'input" |
| **Credentials** | Il login del servizio (es. API key SmartLead) — n8n lo salva cifrato |
| **$json** | I dati che arrivano nel nodo corrente |
| **$node["NomeNodo"].json** | I dati che sono usciti da un nodo precedente specifico |
| **$input.all()** | Tutti gli elementi in ingresso (se il passo precedente ha prodotto più record) |
| **$input.first()** | Il primo elemento in ingresso |
| **Splitting In Batches** | "Dividi in gruppi piccoli e processa gruppo per gruppo" (evita rate limit) |
| **Merge node** | Unisce output di due rami del workflow |
| **Switch node** | Decide quale ramo seguire in base a una condizione (if/else evoluto) |
| **IF node** | Semplice if/else binario |
| **Loop** | Ripeti un'azione per ogni elemento in una lista |
| **Wait node** | Aspetta N secondi/minuti prima di proseguire (per rate limiting) |
| **HTTP Request** | Chiama un'API esterna (al posto di usare il nodo ufficiale del servizio, se non esiste) |
| **Execute Workflow** | Richiama un altro workflow come fosse una "subroutine" |
| **Error Trigger** | Parte automaticamente quando un workflow fallisce (per alert, log) |
| **Active (toggle)** | "Accende" il workflow — prima in `runtime` (test), poi `active` (in produzione) |
| **Execution** | Una singola esecuzione del workflow (con input, output, log) |
| **Test workflow** | Esegue il workflow una volta con dati di esempio, senza "accenderlo" |
| **Pin data** | Blocca i dati di un nodo per test deterministici |

## Anti-pattern (cosa NON dire al pubblico non-dev)

Evita:
- ❌ "Fai parsing del JSON" → ✅ "Estrai i campi dal dato ricevuto"
- ❌ "Endpoint REST" → ✅ "Indirizzo web dove il servizio risponde"
- ❌ "Payload" → ✅ "Contenuto del messaggio"
- ❌ "Async execution" → ✅ "Esegue in background, senza farti aspettare"
- ❌ "Idempotent" → ✅ "Eseguirlo 2 volte produce lo stesso risultato (no duplicati)"
- ❌ "Race condition" → ✅ "Due processi che si pestano i piedi sullo stesso dato"

## Gotchas da spiegare come "tranelli da evitare"

1. **Webhook data è in `$json.body`, non `$json`** — "Se stai leggendo webhook, i dati veri sono sotto `$json.body`. È una gotcha specifica n8n".

2. **Code node return format** — "Il Code node deve restituire un array con dentro oggetti `json`. Se restituisci solo `{...}` direttamente, non funziona. Formato giusto: `return [{json: {campo: valore}}]`".

3. **Python ha limiti** — "Python in n8n Code node non ha librerie esterne (no requests, no pandas). Per 95% dei casi usa JavaScript che ha `$helpers.httpRequest()`".

4. **Credentials non nel codice** — "MAI scrivere API key nel Code node. Sempre via Credentials manager, cifrato".

5. **nodeType mismatch** — "Se stai costruendo workflow via API/MCP, distingui `nodes-base.webhook` (senza prefisso n8n) vs `n8n-nodes-base.webhook` (versione deprecated). Usa quello che il tuo n8n accetta".
