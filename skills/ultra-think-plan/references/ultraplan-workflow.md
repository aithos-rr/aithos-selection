# /ultraplan — Cloud plan mode workflow

`/ultraplan` è un comando Claude Code che sposta il planning in una sandbox Anthropic cloud. Il plan viene generato in background, l'utente può rivederlo in browser con commenti inline, e poi scegliere se eseguirlo remoto (con PR automatica) o portarlo in locale.

## Contents

- [Quando usarlo](#quando-usarlo)
- [Quando NON usarlo](#quando-non-usarlo)
- [Flow completo](#flow-completo)
- [Differenze con plan mode locale](#differenze-con-plan-mode-locale)
- [Integrazione con ultrathink](#integrazione-con-ultrathink)
- [Costo e limiti](#costo-e-limiti)

## Quando usarlo

Adatto quando:

- Il problema è già ben definito (non serve iterare sulla formulazione)
- Servono alternative multiple e una review strutturata prima di eseguire
- Il task è grosso abbastanza da giustificare una sandbox remota
- Si vuole la PR automatica sull'eseguibile (feature di cloud mode)
- Il plan deve essere condiviso con un team o committente per approval

## Quando NON usarlo

Evitare se:

- Il problema è piccolo (≤ 2 file, soluzione ovvia): meglio plan mode locale o risposta diretta
- Serve iterazione rapida sul brief (cloud è batch, non dialogico)
- L'ambiente ha file locali sensibili che la sandbox non può accedere (.env, credenziali, config locali)
- Il piano Anthropic non ha credit sufficiente (cloud plan consuma)

## Flow completo

### Step 1 — Preparazione locale

Prima di invocare `/ultraplan`:

- Descrivere il problema in termini concreti (cosa, perché, vincoli)
- Elencare i file rilevanti (cartelle, moduli, librerie)
- Anticipare i trade-off attesi

Esempio di prompt ben formato:

```text
/ultraplan Refactor autenticazione da JWT a session-based.
Obiettivo: rispettare nuovi requisiti compliance (legal, GDPR).
Vincoli: zero downtime, 50k utenti attivi.
File coinvolti: auth/*.ts, middleware/auth.ts, api/session/.
Alternative da considerare: 1) big bang, 2) dual-auth temporaneo, 3) feature flag progressivo.
```

### Step 2 — Lancio del comando

Invocare `/ultraplan <prompt>` in Claude Code CLI.

Cosa succede:

1. Claude Code apre una sessione cloud nella sandbox Anthropic
2. Viene restituito un URL browser
3. Il plan inizia a generarsi in background

### Step 3 — Review browser

Aprire l'URL ricevuto. L'interfaccia web mostra:

- Plan completo con struttura sezionata
- Alternative valutate con pro/contro
- Fasi di esecuzione con stima tempi
- Sezione Verification
- Possibilità di commentare inline su ogni sezione

### Step 4 — Decisione

Dopo la review, scegliere tra:

- Esecuzione remota: la sandbox Anthropic esegue il plan, apre una PR sul repository GitHub collegato
- Download locale: scaricare il plan (formato markdown) e riprendere con Claude Code locale

### Step 5 — Esecuzione

Per esecuzione remota:

- Connettere il repository GitHub (OAuth)
- Approvare l'esecuzione nella UI web
- La sandbox esegue, testa, crea la PR
- Review umana della PR in GitHub

Per esecuzione locale:

- Aprire il plan scaricato in Claude Code
- Lanciare `/plan-execute` o simile per seguire il plan step by step
- Possibilità di iterare in locale se emergono imprevisti

## Differenze con plan mode locale

| Dimensione | Plan mode locale | `/ultraplan` cloud |
| --- | --- | --- |
| Latenza | Immediato | ~1-5 minuti |
| Iterazione | Dialogica (chat) | Review one-shot + commenti |
| Accesso file | File locali completi | Sandbox isolata (no local secrets) |
| Esecuzione | Manuale locale | Opzione PR automatica |
| Costo | Normale Claude Code | Credit Anthropic separati |
| Team review | Difficile condividere | URL browser shareable |

## Integrazione con ultrathink

I due tool sono complementari:

- `ultrathink` attiva thinking budget esteso su una singola risposta (profondità in un turno)
- `/ultraplan` sposta il planning in cloud (lunghezza e review su più turni)

Pattern combinato:

1. In locale, usare `ultrathink` per capire il problema e identificare se vale `/ultraplan`
2. Se sì, formulare un prompt chiaro e invocare `/ultraplan`
3. Review del plan cloud con team / stakeholder
4. Esecuzione (remota o locale) con la fase 4 di verification applicata

## Costo e limiti

- Cloud plan consuma credit Anthropic dal piano dell'utente
- La sandbox può non avere accesso a dipendenze private / API key locali
- Tempo di generazione: variabile, da 1 a 5-10 minuti per plan complessi
- Per task molto semplici, il costo cloud non è giustificato: meglio plan mode locale

---
_Fonti: [stevekinney — Claude ultraplan](https://stevekinney.com/writing/claude-ultraplan), [docs Anthropic skills](https://code.claude.com/docs/en/skills)._
